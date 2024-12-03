from rest_framework import serializers

from team.serializers import TeamInfoSerializer
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
