# board/serializers.py
from rest_framework import serializers
from .models import *

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'category','created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class BoothEventSerializer(serializers.ModelSerializer):
    booth_id = serializers.IntegerField(source='booth.id', read_only=True)
    booth_name = serializers.CharField(source='booth.admin.name', read_only=True)
    category = serializers.CharField(source='category', read_only=True)

    class Meta:
        model = BoothEvent
        fields = ['id', 'category','booth_id', 
                    'booth_name','title', 'detail', 
                    'start_time', 'end_time',
                    'created_at', 'updated_at']

    def create(self, validated_data):
        return BoothEvent.objects.create(**validated_data)
