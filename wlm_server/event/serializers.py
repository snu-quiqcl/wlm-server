from rest_framework import serializers

from .models import Event

class EventSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'category',
            'content',
            'occurred_at'
        )

    def get_category(self, obj: Event):
        return obj.get_category_display()
