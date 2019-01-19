from rest_framework import serializers

from delivery.models import DeliveryTask

class DeliveryTaskSerializer(serializers.ModelSerializer):
    priority = serializers.CharField(source='get_priority_display')
    state = serializers.CharField(source='get_state_display')

    class Meta:
        model = DeliveryTask
        fields = ('title', 'priority' , 'state', 'id' )