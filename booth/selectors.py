from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Exists, OuterRef, Q, Value, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce
from booth.models import Booth, BoothSchedule, Like


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
                    ordering="auto", top_liked_3=False):

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

     # 현재 이벤트 여부
     qs = qs.annotate(has_event_now=Coalesce("is_event", Value(False)))

     # 거리 계산
     if user_location and "x" in user_location and "y" in user_location:
          qs = qs.annotate(
               distance_m=ExpressionWrapper(
                    ((F("location__map_x") - user_location["x"]) ** 2 +
                    (F("location__map_y") - user_location["y"]) ** 2) ** 0.5,
                    output_field=FloatField()
               )
          )
          ordering = "distance_m"

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
