from rest_framework import serializers
from drf_polymorphic.serializers import PolymorphicSerializer
from django.utils import timezone

from .models import *

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'category', 'writer', 'created_at', 'updated_at']
    
    def get_writer(self, obj):
        request = self.context.get("request")
        if not request:
            return None

        # token 가져오기 (POST/PUT -> data, GET -> query_params)
        token = request.data.get("token") or request.query_params.get("token")
        if not token:
            return None

        try:
            admin = Admin.objects.get(code=token)
            return admin.name
        except Admin.DoesNotExist:
            return None

class NoticeSerializer(BoardSerializer):
    class Meta(BoardSerializer.Meta):
        model = Notice
        fields = ['id', 'category', 'title', 'content', 'is_emergency', 'writer']

class LostSerializer(BoardSerializer):
    class Meta(BoardSerializer.Meta):
        model = Lost
        fields = ['id', 'category', 'title', 'content', 'location', 'image', 'writer']

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

class BoothEventSerializer(BoardSerializer):
    booth_id = serializers.IntegerField(source='booth.id', read_only=True)
    booth_name = serializers.CharField(source='booth.admin.name', read_only=True)
    category = serializers.CharField(source='category', read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = BoothEvent
        fields = BoardSerializer.Meta.fields +['booth_id', 
                    'booth_name','title', 'detail', 
                    'start_time', 'end_time']

    def create(self, validated_data):
        return BoothEvent.objects.create(**validated_data)
    
    def get_is_active(self, obj):
        now = timezone.now()
        return obj.endtime > now
    
class BoardPolymorphicSerializer(PolymorphicSerializer):
    serializer_mapping = {
        Notice: NoticeSerializer,
        Lost: LostSerializer,
        BoothEvent: BoothEventSerializer,
    }