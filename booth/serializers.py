from rest_framework import serializers
from .models import Booth


class ToiletDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booth
        fields = [
            "id",
            "name",
            "image_url",
        ]
