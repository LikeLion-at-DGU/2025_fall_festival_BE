<<<<<<< HEAD
# API 입출력 형태를 결정
from rest_framework import serializers
from drf_polymorphic.serializers import PolymorphicSerializer
=======
# board/serializers.py
from rest_framework import serializers
>>>>>>> 465ea7eed585c7d637fc43beb5f2b7494211757b
from .models import *

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
<<<<<<< HEAD
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']

class NoticeSerializer(BoardSerializer):
    class Meta(BoardSerializer.Meta):
        model = Notice

class LostSerializer(BoardSerializer):
    class Meta(BoardSerializer.Meta):
        model = Lost

class BoardPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Notice: NoticeSerializer,
        Lost: LostSerializer,
    }

# class BoardListSerializer(serializers.ModelSerializer):

#   # admin_id = serializers.SerializerMethodField(read_only=True)
#   # admin_name = serializers.SerializerMethodField(read_only=True)
#   # booth_id = serializers.SerializerMethodField(read_only=True)
#   # booth_name = serializers.SerializerMethodField(read_only=True)
#   category = serializers.SerializerMethodField()

#   class Meta:
#     model = Board
#     fields = [
#       "id",
#       "title",
#       "content",
#       "category",
#       "created_at",
#     ]
#     read_only_fields = ['id', 'created_at']

#   def get_category(self, obj):
#       return obj.__class__.__name__
  
=======
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
>>>>>>> 465ea7eed585c7d637fc43beb5f2b7494211757b
