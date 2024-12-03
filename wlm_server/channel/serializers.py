from django.conf import settings
from rest_framework import serializers

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
        operations = settings.CHANNEL_CACHE.get_operations(obj.channel)
        username = self.context['username']
        try:
            operation = operations[username]
        except KeyError:
            return False
        return operation.on
