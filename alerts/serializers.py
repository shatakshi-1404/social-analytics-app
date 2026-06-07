# alerts/serializers.py
from rest_framework import serializers
from .models import Alert, AlertEvent


class AlertSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    event_count = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = ['id', 'name', 'topic', 'topic_name', 'alert_type',
                  'threshold', 'email', 'is_active', 'created_at', 'event_count']

    def get_event_count(self, obj):
        return obj.events.count()


class AlertEventSerializer(serializers.ModelSerializer):
    alert_name = serializers.CharField(source='alert.name', read_only=True)
    topic_name = serializers.CharField(source='alert.topic.name', read_only=True)

    class Meta:
        model = AlertEvent
        fields = ['id', 'alert', 'alert_name', 'topic_name',
                  'triggered_at', 'triggered_value', 'message', 'is_read']