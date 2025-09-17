from rest_framework import serializers
from .models import *

class DrinkMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["name", "price", "image_url"]


class DrinkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoothSchedule
        fields = ["day", "start_time", "end_time"]


class DrinkDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name") 
    menus = DrinkMenuSerializer(source="menu_set", many=True, read_only=True)
    schedules = DrinkScheduleSerializer(source="boothschedule_set", many=True, read_only=True)

    class Meta:
        model = Booth
        fields = [
            "id",
            "name",
            "image_url",
            "location_name",
            "menus",
            "schedules",
        ]


class ToiletDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booth
        fields = [
            "id",
            "name",
            "image_url",
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name"]


class BoothListSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    likes_count = serializers.IntegerField()
    is_liked = serializers.BooleanField()
    has_event_now = serializers.BooleanField()
    today_open_time = serializers.SerializerMethodField()
    today_close_time = serializers.SerializerMethodField()
    is_open_now = serializers.SerializerMethodField()
    distance_m = serializers.SerializerMethodField()

    class Meta:
        model = Booth
        fields = [
            "id", "name", "category", "image_url", "is_night",
            "is_dorder",
            "location",
            "today_open_time", "today_close_time", "is_open_now",
            "likes_count", "is_liked", "has_event_now",
            "distance_m"
        ]

    def get_today_open_time(self, obj):
        schedule = obj.boothschedule_set.first()
        return schedule.start_time if schedule else None

    def get_today_close_time(self, obj):
        schedule = obj.boothschedule_set.first()
        return schedule.end_time if schedule else None

    def get_is_open_now(self, obj):
        from django.utils import timezone
        now = timezone.localtime().time()
        schedule = obj.boothschedule_set.first()
        return schedule and schedule.start_time <= now <= schedule.end_time

    def get_distance_m(self, obj: Booth):
        distance = getattr(obj, "distance_m", None)

        if distance is None:
            return None
        # 정수 변환
        try:
            return int(round(float(distance)))
        except (TypeError, ValueError):
            # 타입이 이상하면 안전하게 None
            return None