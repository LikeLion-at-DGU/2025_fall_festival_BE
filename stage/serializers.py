from rest_framework import serializers
from .models import Stage

class StageSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Stage
        fields = [
            "id", "name", "start_time", 
            "end_time", "is_active", 
            "image_url", "location_name"
        ]

    def get_is_active(self, obj):
        return obj.is_active
