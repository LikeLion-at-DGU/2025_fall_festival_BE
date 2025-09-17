from rest_framework import serializers
from drf_polymorphic.serializers import PolymorphicSerializer
from .models import *

class BoardSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'category', 'writer']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    # 구현 필요! uid와 비교하여 adminuser 이름 넣어주기
    def get_writer(self, obj):
        if hasattr(obj, "adminuser") and obj.adminuser:
            return obj.adminuser.name
        return None

class NoticeSerializer(BoardSerializer):
    class Meta(BoardSerializer.Meta):
        model = Notice
        fields = ['id', 'category', 'title', 'content', 'is_emergency', 'writer']

class LostSerializer(BoardSerializer):
    class Meta(BoardSerializer.Meta):
        model = Lost
        fields = ['id', 'category', 'title', 'content', 'location', 'image', 'writer']

# class BoardPolymorphicSerializer(PolymorphicSerializer):

#     serializer_mapping = {
#         Notice: NoticeSerializer,
#         Lost: LostSerializer,
#     }

class NoticeListSerializer(BoardSerializer):
    class Meta(BoardSerializer.Meta):
        model = Notice
        fields = ['id', 'category', 'title', 'writer']


class LostListSerializer(BoardSerializer):
    class Meta(BoardSerializer.Meta):
        model = Lost
        fields = ['id', 'category', 'title', 'writer']

class BoardListSerializer(serializers.Serializer):

    def to_representation(self, instance):
        data = None
        if isinstance(instance, Notice):
            data = NoticeListSerializer(instance).data
        elif isinstance(instance, Lost):
            data = LostListSerializer(instance).data
        else:
            data = super().to_representation(instance)

        data.pop("polymorphic_ctype", None)
        return data

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