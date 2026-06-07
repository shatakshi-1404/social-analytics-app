from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)
    keywords = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TweetData(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tweets')
    tweet_id = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    author_id = models.CharField(max_length=100)
    retweet_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.topic.name} - {self.tweet_id}"


class YouTubeVideo(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='videos')
    video_id = models.CharField(max_length=100, unique=True)
    title = models.TextField()
    description = models.TextField(blank=True)
    channel_title = models.CharField(max_length=200)
    view_count = models.BigIntegerField(default=0)
    like_count = models.BigIntegerField(default=0)
    comment_count = models.BigIntegerField(default=0)
    published_at = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return f"{self.topic.name} - {self.title[:50]}"


class TrendSummary(models.Model):
    PLATFORM_CHOICES = [
        ('twitter', 'Twitter'),
        ('youtube', 'YouTube'),
        ('combined', 'Combined'),
    ]
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
        ('mixed', 'Mixed'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='summaries')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    summary_text = models.TextField()
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    sentiment_score = models.FloatField(default=0.0)  # -1 to 1
    key_themes = models.JSONField(default=list)
    trending_keywords = models.JSONField(default=list)
    engagement_score = models.FloatField(default=0.0)
    data_points_count = models.IntegerField(default=0)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.topic.name} - {self.platform} - {self.generated_at.date()}"


class EngagementMetric(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='metrics')
    platform = models.CharField(max_length=20)
    date = models.DateField()
    total_posts = models.IntegerField(default=0)
    total_likes = models.BigIntegerField(default=0)
    total_shares = models.BigIntegerField(default=0)
    total_comments = models.BigIntegerField(default=0)
    avg_engagement = models.FloatField(default=0.0)
    sentiment_positive = models.FloatField(default=0.0)
    sentiment_negative = models.FloatField(default=0.0)
    sentiment_neutral = models.FloatField(default=0.0)

    class Meta:
        unique_together = ['topic', 'platform', 'date']
        ordering = ['-date']