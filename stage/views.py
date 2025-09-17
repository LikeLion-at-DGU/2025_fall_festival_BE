from datetime import datetime
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Stage
from .serializers import StageSerializer

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
        qs = self.queryset.filter(start_time__lte=target, end_time__gt=target)

        return Response({
            "day": day,
            "time": time,
            "schedules": self.get_serializer(qs, many=True).data
        })