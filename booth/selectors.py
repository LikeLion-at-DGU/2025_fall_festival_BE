from django.utils import timezone
from django.db.models import Count, Exists, OuterRef, Q, Value
from django.db.models.functions import Coalesce
from booth.models import Booth, BoothSchedule, Like

#Booth 목록 조회용 selector
def get_booth_list(date=None, types=None, building_id=None,
                    user_location=None, has_event_history=False,
                    ordering="auto", top_liked_3=False):
     
     now = timezone.localtime()
     if not date:
          date = now.date()

     qs = Booth.objects.all().select_related("location")

     # 날짜 기준 스케줄 필터
     qs = qs.filter(
          boothschedule__day=date
     ).distinct()

     # 종류 필터
     if types:
          qs = qs.filter(category__in=types)

     # 건물 필터
     if building_id:
          qs = qs.filter(location_id=building_id)

     # 현재 이벤트 여부
     # TODO: is_event 판별로직 필요 
     qs = qs.annotate(has_event_now=Coalesce("is_event", Value(False)))

     # 거리 계산 (drink/store만)
     if user_location and types and any(t in ["Drink", "Store"] for t in types):
          # TODO: 실제 haversine distance 계산 필요
          from django.db.models import F
          qs = qs.annotate(
               distance_m=((F("location__latitude") - user_location["lat"]) ** 2 +
                         (F("location__longitude") - user_location["lng"]) ** 2)
          )
          ordering = "distance_m"

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
