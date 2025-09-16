# API 입출력 형태를 결정
from rest_framework import serializers
from drf_polymorphic.serializers import PolymorphicSerializer
from .models import *

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
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
  