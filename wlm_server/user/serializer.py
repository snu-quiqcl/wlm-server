from rest_framework import serializers

from team.serializer import TeamInfoSerializer
from .models import User

class UserInfoSerializer(serializers.ModelSerializer):
    team = TeamInfoSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'team',
        )
