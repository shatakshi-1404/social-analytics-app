from django.db import models
from analytics.models import Topic


class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('sentiment_drop', 'Sentiment Drop'),
        ('engagement_spike', 'Engagement Spike'),
        ('volume_spike', 'Volume Spike'),
        ('keyword_mention', 'Keyword Mention'),
    ]

    name = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    threshold = models.FloatField(help_text="Threshold value that triggers the alert")
    email = models.EmailField(blank=True, help_text="Email for notifications")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.alert_type})"


class AlertEvent(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='events')
    triggered_at = models.DateTimeField(auto_now_add=True)
    triggered_value = models.FloatField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-triggered_at']

    def __str__(self):
        return f"{self.alert.name} - {self.triggered_at}"