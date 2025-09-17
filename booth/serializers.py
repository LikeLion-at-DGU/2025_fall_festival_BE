from rest_framework import serializers
from .models import Booth, Menu, BoothSchedule

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["name", "price", "image_url"]


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoothSchedule
        fields = ["day", "start_time", "end_time"]


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
