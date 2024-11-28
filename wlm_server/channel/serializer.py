from rest_framework import serializers

from .models import Channel
from operation.models import Operation

class ChannelInfoSerializer(serializers.ModelSerializer):
    operation = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = (
            'channel',
            'name',
            'operation',
        )

    def get_operation(self, obj: Channel):
        user = self.context['user']
        try:
            operation = Operation.objects.filter(user=user, channel=obj).latest('occurred_at')
        except Operation.DoesNotExist:
            return False
        return operation.on
