from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Value, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from booth.models import *
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
     """
     위도, 경도(도 단위) → 실제 거리 반환

     [매개변수]
     - lat1, lon1: 기준점(x, y) → 위도, 경도 값이라고 가정
     - lat2, lon2: 대상점(부스)의 위도/경도 (도 단위)

     [반환값]
     - 거리(meter, float)
     """
     R = 6371000  # 지구 반지름(m)
     dlat = radians(lat2 - lat1)
     dlon = radians(lon2 - lon1)
     a = sin(dlat/2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) ** 2
     c = 2 * atan2(sqrt(a), sqrt(1 - a))
     return R * c



def get_foodtruck_detail(booth_id: int) -> Booth:
     """
     category가 FoodTruck인 booth 상세정보 반환
     """
     booth = get_object_or_404(
          Booth.objects.select_related("location")
          .prefetch_related("menu_set", "boothschedule_set"),
          id=booth_id
     )
     if booth.category != Booth.Category.FOODTRUCK:
          raise ValueError("요청한 부스의 카테고리가 푸드트럭이 아님")
     return booth


def get_drink_detail(booth_id: int) -> Booth:
     """
     category가 Drink인 booth 상세정보 반환
     """
     booth = get_object_or_404(Booth, id=booth_id)
     if booth.category != Booth.Category.DRINK:
          raise ValueError("요청한 부스의 카테고리가 주류 판매가 아님")
     return booth


def get_toilet_detail(booth_id: int) -> Booth:
     """
     category가 Toilet인 booth 상세정보 반환
     """
     booth = get_object_or_404(Booth, id=booth_id)
     if booth.category != Booth.Category.TOILET:
          raise ValueError("요청한 부스의 카테고리가 화장실이 아님")
     return booth

#Booth 목록 조회용 selector
def get_booth_list(date=None, types=None, building_id=None, user_location=None,
                    ordering="auto", top_liked_3=False, is_night=None):

     if not date:
          date = timezone.localdate()

     qs = Booth.objects.all().select_related("location")
     qs = qs.filter(operate_date=date)

     # 종류 필터
     if types:
          qs = qs.filter(category__in=types)

     # 건물 필터
     if building_id:
          qs = qs.filter(location_id=building_id)

     # 낮/밤 부스 필터
     if is_night is not None:
          qs = qs.filter(is_night=is_night)

     booths = list(qs)

     # 거리 계산
     if user_location and "x" in user_location and "y" in user_location:
          user_lat = user_location["x"]
          user_lon = user_location["y"]

          for booth in booths:
               if booth.location and booth.location.latitude and booth.location.longitude:
                    booth.distance_m = calculate_distance(
                         user_lat, user_lon,
                         booth.location.latitude, booth.location.longitude
                    )
               else:
                    booth.distance_m = None
          # 정렬 조건
          if ordering == "distance":
               booths.sort(key=lambda b: b.distance_m if b.distance_m is not None else float("inf"))
     else:
          if ordering == "name":
               booths.sort(key=lambda b: b.name)
          elif ordering == "-name":
               booths.sort(key=lambda b: b.name, reverse=True)
          else:
               booths.sort(key=lambda b: b.name)

     #TODO: 좋아요 count + 현재 사용자 좋아요 여부 annotate 필요

     if top_liked_3:
          booths = booths[:3]

     return booths
