from rest_framework import serializers

from .models import Channel

class ChannelInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'channel',
            'name',
        )
