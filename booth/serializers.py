from rest_framework import serializers
from django.utils import timezone

from rest_framework import serializers
from .models import *
from board.models import *

class LocationSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(source="latitude")
    lng = serializers.FloatField(source="longitude")

    class Meta:
        model = Location
        fields = ["id", "name", "lat", "lng"]

class BoothListSerializer(serializers.ModelSerializer):
    booth_id = serializers.IntegerField(source="id")
    event_id = serializers.SerializerMethodField()

    location = LocationSerializer()
    like_cnt = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_event = serializers.BooleanField()
    business_days = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    distance_m = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Booth
        fields = [
            "booth_id",
            "name","category",
            "image_url",
            "is_night","is_dorder","is_event", "event_id",
            "location", "distance_m",
            "business_days","start_time","end_time",
            "like_cnt", "is_liked",
        ]

    def get_event_id(self, obj):
        if not obj.is_event:
            return None
        
        now = timezone.now()
        event = (
            BoothEvent.objects
            .filter(
                booth=obj,
                category=Board.Category.EVENT,
                start_time__lte=now,
                end_time__gte=now
            )
            .order_by("start_time")
            .first()
        )
        return event.id if event else None

    def get_image_url(self, obj):
        if obj.image_url:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image_url.url)
        return None

    def get_business_days(self, obj):
        schedules = obj.boothschedule_set.order_by("day", "start_time")
        return ScheduleSerializer(schedules, many=True).data
        
    def _get_schedule_for_date(self, obj: Booth):
        date = self.context.get("date", timezone.localdate())
        return obj.boothschedule_set.filter(day=date).order_by("start_time").first()
    
    def get_like_cnt(self, obj):
        return obj.like_cnt

    def get_is_liked(self, obj):
        return False

    def get_start_time(self, obj):
        first_schedule = obj.boothschedule_set.order_by("start_time").first()
        return first_schedule.start_time.strftime("%H:%M") if first_schedule else None

    def get_end_time(self, obj):
        last_schedule = obj.boothschedule_set.order_by("-end_time").first()
        return last_schedule.end_time.strftime("%H:%M") if last_schedule else None

    def get_distance_m(self, obj: Booth):
        distance = getattr(obj, "distance_m", None)
        if distance is None:
            return None
        try:
            return int(round(float(distance)))
        except (TypeError, ValueError):
            return None

##################################################################
class MenuSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ["name", "price", "image_url"]

    def get_image_url(self, obj):
        if obj.image_url:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image_url.url)
        return None

class DorderMenuSerializer(serializers.ModelSerializer):
    is_best = serializers.SerializerMethodField()
    is_soldout = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

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
        if obj.ingredient is not None:
            return obj.ingredient < 5
        return False 

    def get_image_url(self, obj):
        if obj.image_url:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image_url.url)
        return None

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
    image_url = serializers.SerializerMethodField()

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
        
    def get_image_url(self, obj):
        if obj.image_url:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image_url.url)
        return None

class NightBoothDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True)
    location_description = serializers.CharField(source="location.description", read_only=True)
    schedules = ScheduleSerializer(source="boothschedule_set", many=True, read_only=True)
    menus = serializers.SerializerMethodField()
    booth_description = serializers.CharField(source="boothdetail.description", read_only=True)
    booth_can_usage = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

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
    
    def get_image_url(self, obj):
        if obj.image_url:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image_url.url)
        return None
    
    def get_menus(self, obj):
        request = self.context.get("request")
        menus = list(obj.menu_set.all())

        if obj.is_dorder:
            # Dorder 부스 → '입장료' 맨 앞으로
            sorted_menus = sorted(menus, key=lambda x: "입장료" not in x.name)
            return DorderMenuSerializer(sorted_menus, many=True, context={"request": request}).data
        else:
            # 일반 부스 → 기본 
            sorted_menus = sorted(menus, key=lambda x: "입장료" not in x.name)
            return MenuSerializer(sorted_menus, many=True, context={"request": request}).data

    def get_booth_can_usage(self, obj):
        if not obj.is_dorder:
            return None
        return obj.boothdetail.dynamic_can_usage

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     request = self.context.get("request")
    #     if not instance.is_dorder:
    #         rep.pop("booth_can_usage", None)
    #         rep["menus"] = MenuSerializer(instance.menu_set.all(), many=True, context={"request": request}).data
    #     else:
    #         rep["menus"] = DorderMenuSerializer(instance.menu_set.all(), many=True, context={"request": request}).data

    #     return rep
    
class DrinkDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True) 
    location_description = serializers.CharField(source="location.description", read_only=True) 
    menus = MenuSerializer(source="menu_set", many=True, read_only=True)
    schedules = ScheduleSerializer(source="boothschedule_set", many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

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

    def get_image_url(self, obj):
        if obj.image_url:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image_url.url)
        return None

class FoodtruckDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True) 
    location_description = serializers.CharField(source="location.description", read_only=True) 
    menus = MenuSerializer(source="menu_set", many=True, read_only=True)
    schedules = ScheduleSerializer(source="boothschedule_set", many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

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

    def get_image_url(self, obj):
        if obj.image_url:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image_url.url)
        return None
        
class ToiletDetailSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source="location.name", read_only=True) 
    location_description = serializers.CharField(source="location.description", read_only=True) 
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Booth
        fields = [
            "id",
            "name",
            "image_url",
            "location_name",
            "location_description",
        ]

    def get_image_url(self, obj):
        if obj.image_url:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image_url.url)
        return None


class DrinkMenuSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField() 
    class Meta:
        model = Menu
        fields = ["name", "price", "image_url"]

    def get_image_url(self, obj):
        if obj.image_url:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image_url.url)
        return None