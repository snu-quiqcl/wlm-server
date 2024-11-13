from rest_framework import serializers

from .models import User
from team.serializer import TeamInfoSerializer

class UserInfoSerializer(serializers.ModelSerializer):
    team = TeamInfoSerializer()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "team",
        )
