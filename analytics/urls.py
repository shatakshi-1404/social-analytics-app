from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TopicViewSet, TweetDataViewSet, YouTubeVideoViewSet,
    TrendSummaryViewSet, EngagementMetricViewSet, DashboardViewSet
)

router = DefaultRouter()
router.register(r'topics', TopicViewSet)
router.register(r'tweets', TweetDataViewSet)
router.register(r'videos', YouTubeVideoViewSet)
router.register(r'summaries', TrendSummaryViewSet)
router.register(r'metrics', EngagementMetricViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]