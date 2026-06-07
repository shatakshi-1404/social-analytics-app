from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Alert, AlertEvent
from .serializers import AlertSerializer, AlertEventSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        alerts = Alert.objects.filter(is_active=True)
        return Response(AlertSerializer(alerts, many=True).data)


class AlertEventViewSet(viewsets.ModelViewSet):
    queryset = AlertEvent.objects.all().order_by('-triggered_at')
    serializer_class = AlertEventSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        alert_id = self.request.query_params.get('alert_id')
        unread = self.request.query_params.get('unread')
        if alert_id:
            qs = qs.filter(alert_id=alert_id)
        if unread == 'true':
            qs = qs.filter(is_read=False)
        return qs

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        AlertEvent.objects.filter(is_read=False).update(is_read=True)
        return Response({'message': 'All events marked as read'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        event = self.get_object()
        event.is_read = True
        event.save()
        return Response({'message': 'Event marked as read'})