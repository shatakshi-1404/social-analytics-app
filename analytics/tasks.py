from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def fetch_topic_data(self, topic_id: int):
    """Fetch fresh Twitter and YouTube data for a topic."""
    from .models import Topic, TweetData, YouTubeVideo
    from .services.twitter_service import TwitterService
    from .services.youtube_service import YouTubeService

    try:
        topic = Topic.objects.get(id=topic_id)
        query = topic.name + (" " + " OR ".join(topic.keywords) if topic.keywords else "")

        # Fetch Twitter data
        twitter = TwitterService()
        tweets = twitter.search_recent_tweets(query, max_results=50)
        tweet_count = 0
        for raw_tweet in tweets:
            parsed = twitter.parse_tweet(raw_tweet)
            _, created = TweetData.objects.update_or_create(
                tweet_id=parsed['tweet_id'],
                defaults={**parsed, 'topic': topic}
            )
            if created:
                tweet_count += 1

        # Fetch YouTube data
        youtube = YouTubeService()
        videos = youtube.search_videos(topic.name, max_results=15)
        video_count = 0
        for raw_video in videos:
            parsed = youtube.parse_video(raw_video)
            if parsed['video_id']:
                _, created = YouTubeVideo.objects.update_or_create(
                    video_id=parsed['video_id'],
                    defaults={**parsed, 'topic': topic}
                )
                if created:
                    video_count += 1

        logger.info(f"Fetched {tweet_count} tweets and {video_count} videos for topic: {topic.name}")

        # Auto-generate summary after fetch
        generate_topic_summary.delay(topic_id)
        return {'tweets': tweet_count, 'videos': video_count}

    except Topic.DoesNotExist:
        logger.error(f"Topic {topic_id} not found")
    except Exception as exc:
        logger.error(f"Error fetching data for topic {topic_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_topic_summary(self, topic_id: int):
    """Generate AI summary for a topic using Claude."""
    from .models import Topic, TweetData, YouTubeVideo, TrendSummary, EngagementMetric
    from .services.ai_service import AIService
    from django.db.models import Sum, Avg
    import datetime

    try:
        topic = Topic.objects.get(id=topic_id)
        ai = AIService()
        cutoff = timezone.now() - timedelta(hours=24)

        # Analyze Twitter
        recent_tweets = TweetData.objects.filter(topic=topic, created_at__gte=cutoff)
        if recent_tweets.exists():
            tweet_texts = list(recent_tweets.values_list('text', flat=True)[:30])
            twitter_analysis = ai.analyze_trends(topic.name, 'Twitter', tweet_texts)

            TrendSummary.objects.create(
                topic=topic,
                platform='twitter',
                summary_text=twitter_analysis.get('summary', ''),
                sentiment=twitter_analysis.get('sentiment', 'neutral'),
                sentiment_score=twitter_analysis.get('sentiment_score', 0.0),
                key_themes=twitter_analysis.get('key_themes', []),
                trending_keywords=twitter_analysis.get('trending_keywords', []),
                engagement_score=twitter_analysis.get('engagement_score', 0.0),
                data_points_count=recent_tweets.count(),
            )

            # Update engagement metrics
            today = timezone.now().date()
            agg = recent_tweets.aggregate(
                total_likes=Sum('like_count'),
                total_shares=Sum('retweet_count'),
                total_comments=Sum('reply_count'),
            )
            EngagementMetric.objects.update_or_create(
                topic=topic, platform='twitter', date=today,
                defaults={
                    'total_posts': recent_tweets.count(),
                    'total_likes': agg['total_likes'] or 0,
                    'total_shares': agg['total_shares'] or 0,
                    'total_comments': agg['total_comments'] or 0,
                    'avg_engagement': twitter_analysis.get('engagement_score', 0.0),
                    'sentiment_positive': 1.0 if twitter_analysis.get('sentiment') == 'positive' else 0.0,
                    'sentiment_negative': 1.0 if twitter_analysis.get('sentiment') == 'negative' else 0.0,
                    'sentiment_neutral': 1.0 if twitter_analysis.get('sentiment') == 'neutral' else 0.0,
                }
            )

        # Analyze YouTube
        recent_videos = YouTubeVideo.objects.filter(topic=topic, fetched_at__gte=cutoff)
        if recent_videos.exists():
            video_texts = [f"{v.title}: {v.description[:100]}" for v in recent_videos[:20]]
            youtube_analysis = ai.analyze_trends(topic.name, 'YouTube', video_texts)

            TrendSummary.objects.create(
                topic=topic,
                platform='youtube',
                summary_text=youtube_analysis.get('summary', ''),
                sentiment=youtube_analysis.get('sentiment', 'neutral'),
                sentiment_score=youtube_analysis.get('sentiment_score', 0.0),
                key_themes=youtube_analysis.get('key_themes', []),
                trending_keywords=youtube_analysis.get('trending_keywords', []),
                engagement_score=youtube_analysis.get('engagement_score', 0.0),
                data_points_count=recent_videos.count(),
            )

        # Check alerts
        check_topic_alerts.delay(topic_id)
        logger.info(f"Generated summaries for topic: {topic.name}")

    except Topic.DoesNotExist:
        logger.error(f"Topic {topic_id} not found")
    except Exception as exc:
        logger.error(f"Error generating summary for topic {topic_id}: {exc}")
        raise self.retry(exc=exc, countdown=120)


@shared_task
def check_topic_alerts(topic_id: int):
    """Check if any alert thresholds are exceeded."""
    from alerts.models import Alert, AlertEvent
    from .models import Topic, TrendSummary, EngagementMetric

    try:
        topic = Topic.objects.get(id=topic_id)
        active_alerts = Alert.objects.filter(topic=topic, is_active=True)

        latest_summary = TrendSummary.objects.filter(topic=topic).order_by('-generated_at').first()
        latest_metric = EngagementMetric.objects.filter(topic=topic).order_by('-date').first()

        for alert in active_alerts:
            triggered = False
            current_value = 0.0

            if alert.alert_type == 'sentiment_drop' and latest_summary:
                current_value = latest_summary.sentiment_score
                triggered = current_value < alert.threshold
            elif alert.alert_type == 'engagement_spike' and latest_metric:
                current_value = latest_metric.avg_engagement
                triggered = current_value > alert.threshold
            elif alert.alert_type == 'volume_spike' and latest_metric:
                current_value = float(latest_metric.total_posts)
                triggered = current_value > alert.threshold

            if triggered:
                AlertEvent.objects.create(
                    alert=alert,
                    triggered_value=current_value,
                    message=f"Alert '{alert.name}': {alert.alert_type} triggered. Value: {current_value:.2f}, Threshold: {alert.threshold:.2f}",
                )
                logger.info(f"Alert triggered: {alert.name} for topic {topic.name}")

    except Exception as e:
        logger.error(f"Error checking alerts: {e}")


@shared_task
def fetch_all_topics():
    """Scheduled task: fetch data for all active topics."""
    from .models import Topic
    topics = Topic.objects.filter(is_active=True)
    for topic in topics:
        fetch_topic_data.delay(topic.id)
    logger.info(f"Scheduled fetch started for {topics.count()} topics")