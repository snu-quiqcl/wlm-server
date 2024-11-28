from rest_framework import serializers

from operation.models import Operation
from .models import Channel

class ChannelInfoSerializer(serializers.ModelSerializer):
    in_use = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = (
            'channel',
            'name',
            'in_use',
        )

    def get_in_use(self, obj: Channel):
        user = self.context['user']
        try:
            operation = Operation.objects.filter(user=user, channel=obj).latest('occurred_at')
        except Operation.DoesNotExist:
            return False
        return operation.on
