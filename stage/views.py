from datetime import datetime
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Stage
from .serializers import StageSerializer
from datetime import timedelta


class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.select_related("location").order_by("start_time")
    serializer_class = StageSerializer

    #날짜별 공연조회
    @action(detail=False, methods=["get"], url_path=r"days/(?P<day>[^/.]+)/schedules")
    def stage_day(self, request, day=None):
        d = datetime.strptime(day, "%Y-%m-%d").date()
        start_dt = timezone.make_aware(datetime.combine(d, datetime.min.time()))  #00:00:00
        end_dt   = timezone.make_aware(datetime.combine(d, datetime.max.time()))  #23:59:59

        qs = self.queryset.filter(start_time__lte=end_dt, end_time__gte=start_dt)
        return Response({
            "day": day,
            "schedules": self.get_serializer(qs, many=True).data
        })

    # 특정 시간 공연 조회
    @action(detail=False, methods=["get"], url_path=r"days/(?P<day>[^/.]+)/schedules/(?P<time>[^/.]+)")
    def by_day_time(self, request, day=None, time=None):
        target = timezone.make_aware(datetime.strptime(f"{day} {time}", "%Y-%m-%d %H:%M"))
        
        # 해당 시간 ~ 1시간 구간
        start_of_hour = target
        end_of_hour = target + timedelta(hours=1)

        # 공연이 이 구간과 겹치면 조회
        qs = self.queryset.filter(
            start_time__lt=end_of_hour,
            end_time__gt=start_of_hour
        )

        return Response({
            "day": day,
            "time": time,
            "schedules": self.get_serializer(qs, many=True).data
        })