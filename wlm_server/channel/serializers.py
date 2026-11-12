from django.conf import settings
from rest_framework import serializers

from .models import Channel

class ChannelInfoSerializer(serializers.ModelSerializer):
    in_use = serializers.SerializerMethodField()
    has_lock = serializers.SerializerMethodField()
    has_pid = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = (
            'channel',
            'name',
            'in_use',
            'has_lock',
            'has_pid',
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

    def get_has_pid(self, obj: Channel):
        pid_operation = settings.CHANNEL_CACHE.get_pid_operation(obj.channel)
        if pid_operation is None:
            return False
        username = self.context['username']
        return pid_operation.user.username == username
