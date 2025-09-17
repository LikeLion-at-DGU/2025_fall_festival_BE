from rest_framework import serializers
from .models import *


class BoothSerializer(serializers.ModelSerializer):
    pass

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["name", "price", "image_url"]

class DorderMenuSerializer(serializers.ModelSerializer):
    is_best = serializers.SerializerMethodField()
    is_soldout = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ["name", "price", "image_url", "is_best", "is_soldout"]

    def get_is_best(self, obj):
        booth = obj.booth
        # sold 내림차순 + id 오름차순
        top3_ids = (
            booth.menu_set.order_by("-sold", "id")[:3].values_list("id", flat=True)
        )
        return obj.id in top3_ids

    def get_is_soldout(self, obj):
        return obj.ingredient < 5

class CornerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corner
        fields = ["name"]

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoothSchedule
        fields = ["day", "start_time", "end_time"]

class DayBoothDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)
    location_description = serializers.CharField(source="location.description", read_only=True)
    schedules = ScheduleSerializer(source="boothschedule_set", many=True, read_only=True)
    corners = CornerSerializer(source="corner_set", many=True, read_only=True)
    booth_description = serializers.CharField(source="boothdetail.description", read_only=True)

    class Meta:
        model = Booth
        fields = [
            "id",
            "is_night",
            "name",
            "image_url",
            "location_name",
            "location_description",
            "schedules",
            "booth_description",
            "corners",
        ]

class NightBoothDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)
    location_description = serializers.CharField(source="location.description", read_only=True)
    schedules = ScheduleSerializer(source="boothschedule_set", many=True, read_only=True)
    menus = DorderMenuSerializer(source="menu_set", many=True, read_only=True)
    booth_description = serializers.CharField(source="boothdetail.description", read_only=True)
    booth_can_usage = serializers.CharField(source="boothdetail.can_usage", read_only=True)

    class Meta:
        model = Booth
        fields = [
            "id",
            "is_night",
            "name",
            "is_dorder",
            "image_url",
            "location_name",
            "location_description",
            "schedules",
            "booth_description",
            "booth_can_usage",
            "menus",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.is_dorder:
            rep.pop("booth_can_usage", None)
            rep["menus"] = MenuSerializer(instance.menu_set.all(), many=True).data
        else:
            rep["menus"] = DorderMenuSerializer(instance.menu_set.all(), many=True).data

        return rep
        
class DrinkDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True) 
    location_description = serializers.CharField(source="location.description", read_only=True) 
    menus = MenuSerializer(source="menu_set", many=True, read_only=True)
    schedules = ScheduleSerializer(source="boothschedule_set", many=True, read_only=True)

    class Meta:
        model = Booth
        fields = [
            "id",
            "name",
            "image_url",
            "location_name",
            "location_description",
            "menus",
            "schedules",
        ]

class FoodtruckDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True) 
    location_description = serializers.CharField(source="location.description", read_only=True) 
    menus = MenuSerializer(source="menu_set", many=True, read_only=True)
    schedules = ScheduleSerializer(source="boothschedule_set", many=True, read_only=True)

    class Meta:
        model = Booth
        fields = [
            "id",
            "name",
            "image_url",
            "location_name",
            "location_description",
            "menus",
            "schedules",
        ]

class ToiletDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True) 
    location_description = serializers.CharField(source="location.description", read_only=True) 
    
    class Meta:
        model = Booth
        fields = [
            "id",
            "name",
            "image_url",
            "location_name",
            "location_description",
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name"]


class BoothListSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_event = serializers.BooleanField()
    today_open_time = serializers.SerializerMethodField()
    today_close_time = serializers.SerializerMethodField()
    distance_m = serializers.SerializerMethodField()

    class Meta:
        model = Booth
        fields = [
            "id", "name", "category", "image_url", "is_night",
            "is_dorder",
            "location",
            "today_open_time", "today_close_time",
            "likes_count", "is_liked", 
            "is_event",
            "distance_m"
        ]

    def get_likes_count(self, obj):
        # 임시 디폴트값 리턴
        return 0  

    def get_is_liked(self, obj):
        # 임시 디폴트값 리턴
        return False
    
    def _get_schedule_for_date(self, obj: Booth):
        date = self.context.get("date", timezone.localdate())
        return obj.boothschedule_set.filter(day=date).order_by("start_time").first()

    def get_today_open_time(self, obj):
        schedule = self._get_schedule_for_date(obj)
        return schedule.start_time.strftime("%H:%M") if schedule else None

    def get_today_close_time(self, obj):
        schedule = self._get_schedule_for_date(obj)
        return schedule.end_time.strftime("%H:%M") if schedule else None
    
    def get_distance_m(self, obj: Booth):
        distance = getattr(obj, "distance_m", None)
        if distance is None:
            return None
        try:
            return int(round(float(distance)))
        except (TypeError, ValueError):
            return None