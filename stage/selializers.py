from rest_framework import serializers
from .models import Stage

class StageSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)
    is_live_now = serializers.SerializerMethodField()

    class Meta:
        model = Stage
        fields = [
            "id", "name", "start_time", 
            "end_time", "is_live_now", 
            "image_url", "location_name"
        ]

    def get_is_live_now(self, obj):
        return obj.is_live_now
    
    