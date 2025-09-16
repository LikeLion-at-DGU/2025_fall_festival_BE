from rest_framework import serializers
from .models import Booth, Menu, BoothSchedule

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
