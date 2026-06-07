from rest_framework import serializers
from .models import Topic, TweetData, YouTubeVideo, TrendSummary, EngagementMetric


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'keywords', 'is_active', 'created_at']


class TweetDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetData
        fields = ['id', 'tweet_id', 'text', 'author_id', 'retweet_count',
                  'like_count', 'reply_count', 'created_at', 'fetched_at']


class YouTubeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeVideo
        fields = ['id', 'video_id', 'title', 'description', 'channel_title',
                  'view_count', 'like_count', 'comment_count', 'published_at', 'fetched_at']


class TrendSummarySerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)

    class Meta:
        model = TrendSummary
        fields = ['id', 'topic', 'topic_name', 'platform', 'summary_text', 'sentiment',
                  'sentiment_score', 'key_themes', 'trending_keywords',
                  'engagement_score', 'data_points_count', 'generated_at']


class EngagementMetricSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)

    class Meta:
        model = EngagementMetric
        fields = ['id', 'topic', 'topic_name', 'platform', 'date', 'total_posts',
                  'total_likes', 'total_shares', 'total_comments',
                  'avg_engagement', 'sentiment_positive', 'sentiment_negative', 'sentiment_neutral']


class DashboardStatsSerializer(serializers.Serializer):
    total_topics = serializers.IntegerField()
    total_tweets = serializers.IntegerField()
    total_videos = serializers.IntegerField()
    total_summaries = serializers.IntegerField()
    recent_summaries = TrendSummarySerializer(many=True)
    top_topics = TopicSerializer(many=True)