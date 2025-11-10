from django.conf import settings
from rest_framework import serializers

from .models import Channel

class ChannelInfoSerializer(serializers.ModelSerializer):
    in_use = serializers.SerializerMethodField()
    has_lock = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = (
            'channel',
            'name',
            'in_use',
            'has_lock',
        )

    def get_in_use(self, obj: Channel):
        operations = settings.CHANNEL_CACHE.get_operations(obj.channel)
        username = self.context['username']
        try:
            operation = operations[username]
        except KeyError:
            return False
        return operation.on

    def get_has_lock(self, obj: Channel):
        lock = settings.CHANNEL_CACHE.get_lock(obj.channel)
        if lock is None:
            return False
        username = self.context['username']
        return lock.user.username == username
