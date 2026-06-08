from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Topic, TweetData, YouTubeVideo, TrendSummary, EngagementMetric
from .serializers import (
    TopicSerializer, TweetDataSerializer, YouTubeVideoSerializer,
    TrendSummarySerializer, EngagementMetricSerializer, DashboardStatsSerializer
)
from .tasks import fetch_topic_data, generate_topic_summary


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all().order_by('-created_at')
    serializer_class = TopicSerializer

    @action(detail=True, methods=['post'])
def refresh(self, request, pk=None):
    topic = self.get_object()
    try:
        fetch_topic_data.delay(topic.id)
    except Exception:
        # Celery not available — run synchronously
        fetch_topic_data(topic.id)
    return Response({'message': f'Data refresh started for topic: {topic.name}'})

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        topic = self.get_object()
        generate_topic_summary.delay(topic.id)
        return Response({'message': f'AI analysis started for topic: {topic.name}'})

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        topic = self.get_object()
        tweets = TweetData.objects.filter(topic=topic)
        videos = YouTubeVideo.objects.filter(topic=topic)
        summaries = TrendSummary.objects.filter(topic=topic).order_by('-generated_at')[:5]

        return Response({
            'topic': TopicSerializer(topic).data,
            'tweet_count': tweets.count(),
            'video_count': videos.count(),
            'total_tweet_likes': tweets.aggregate(s=Sum('like_count'))['s'] or 0,
            'total_video_views': videos.aggregate(s=Sum('view_count'))['s'] or 0,
            'latest_summaries': TrendSummarySerializer(summaries, many=True).data,
        })


class TweetDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TweetData.objects.all().order_by('-created_at')
    serializer_class = TweetDataSerializer
    filterset_fields = ['topic']

    def get_queryset(self):
        qs = super().get_queryset()
        topic_id = self.request.query_params.get('topic_id')
        if topic_id:
            qs = qs.filter(topic_id=topic_id)
        return qs


class YouTubeVideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = YouTubeVideo.objects.all().order_by('-published_at')
    serializer_class = YouTubeVideoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        topic_id = self.request.query_params.get('topic_id')
        if topic_id:
            qs = qs.filter(topic_id=topic_id)
        return qs


class TrendSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrendSummary.objects.all().order_by('-generated_at')
    serializer_class = TrendSummarySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        topic_id = self.request.query_params.get('topic_id')
        platform = self.request.query_params.get('platform')
        if topic_id:
            qs = qs.filter(topic_id=topic_id)
        if platform:
            qs = qs.filter(platform=platform)
        return qs


class EngagementMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EngagementMetric.objects.all().order_by('-date')
    serializer_class = EngagementMetricSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        topic_id = self.request.query_params.get('topic_id')
        days = int(self.request.query_params.get('days', 7))
        if topic_id:
            qs = qs.filter(topic_id=topic_id)
        cutoff = timezone.now().date() - timedelta(days=days)
        return qs.filter(date__gte=cutoff)


class DashboardViewSet(viewsets.ViewSet):
    def list(self, request):
        topics = Topic.objects.filter(is_active=True)
        recent_summaries = TrendSummary.objects.order_by('-generated_at')[:6]
        data = {
            'total_topics': Topic.objects.count(),
            'total_tweets': TweetData.objects.count(),
            'total_videos': YouTubeVideo.objects.count(),
            'total_summaries': TrendSummary.objects.count(),
            'recent_summaries': TrendSummarySerializer(recent_summaries, many=True).data,
            'top_topics': TopicSerializer(topics[:5], many=True).data,
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def sentiment_chart(self, request):
        """Returns sentiment distribution data for charting."""
        days = int(request.query_params.get('days', 7))
        cutoff = timezone.now() - timedelta(days=days)
        summaries = TrendSummary.objects.filter(generated_at__gte=cutoff)

        sentiment_counts = summaries.values('sentiment').annotate(count=Count('id'))
        return Response(list(sentiment_counts))

    @action(detail=False, methods=['get'])
    def engagement_trend(self, request):
        """Returns engagement trend data for a topic."""
        topic_id = request.query_params.get('topic_id')
        days = int(request.query_params.get('days', 14))
        cutoff = timezone.now().date() - timedelta(days=days)

        qs = EngagementMetric.objects.filter(date__gte=cutoff)
        if topic_id:
            qs = qs.filter(topic_id=topic_id)

        data = qs.values('date', 'platform').annotate(
            avg_engagement=Avg('avg_engagement'),
            total_posts=Sum('total_posts')
        ).order_by('date')
        return Response(list(data))

    @action(detail=False, methods=['post'])
    def refresh_all(self, request):
        """Trigger data refresh for all active topics."""
        topics = Topic.objects.filter(is_active=True)
        for topic in topics:
            fetch_topic_data.delay(topic.id)
        return Response({'message': f'Refresh started for {topics.count()} topics'})