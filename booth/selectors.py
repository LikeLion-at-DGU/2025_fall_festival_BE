from django.utils import timezone
from django.db.models import Value, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from booth.models import *
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(lat1, lon1, lat2, lon2):
     """
     위도, 경도(도 단위) → 실제 거리 반환
     """
     R = 6371000  # 지구 반지름(m)
     dlat = radians(lat2 - lat1)
     dlon = radians(lon2 - lon1)
     a = sin(dlat/2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) ** 2
     c = 2 * atan2(sqrt(a), sqrt(1 - a))
     return R * c


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
     if user_location and "latitude" in user_location and "longitude" in user_location:
          user_lat = user_location["latitude"]
          user_lon = user_location["longitude"]

          for booth in booths:
               if booth.location and booth.location.latitude and booth.location.longitude:
                    booth.distance_m = calculate_distance(
                         user_lat, user_lon,
                         booth.location.latitude, booth.location.longitude
                    )
               else:
                    booth.distance_m = None

     #TODO: 좋아요 count + 현재 사용자 좋아요 여부 annotate 필요

     # ordering 정렬
     if ordering == "name":
          qs = qs.order_by("name")
     elif ordering == "-name":
          qs = qs.order_by("-name")
     elif ordering == "likes":
          qs = qs.order_by("likes_count")
     elif ordering == "-likes":
          qs = qs.order_by("-likes_count")
     elif ordering == "distance" and "distance_m" in [f.name for f in qs.model._meta.get_fields()]:
          qs = qs.order_by("distance_m")
     else:
          qs = qs.order_by("name")

     if top_liked_3:
          qs = qs.order_by("-likes_count")[:3]

     return qs
