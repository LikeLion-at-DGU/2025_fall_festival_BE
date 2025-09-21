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

        # 동아리 공연: 날짜 + 시간
        club_qs = self.queryset.filter(
            type="club",
            start_time__lte=end_dt,
            end_time__gte=start_dt,
        )

        # 연예인 공연: 날짜만
        celebrity_qs = self.queryset.filter(
            type="celebrity",
            start_time__date=d,
        )

        qs = club_qs | celebrity_qs
        return Response({
            "day": day,
            "schedules": self.get_serializer(qs, many=True).data
        })

    # 특정 시간 공연 조회 (동아리만)
    @action(detail=False, methods=["get"], url_path=r"days/(?P<day>[^/.]+)/schedules/(?P<time>[^/.]+)")
    def by_day_time(self, request, day=None, time=None):
        target = timezone.make_aware(datetime.strptime(f"{day} {time}", "%Y-%m-%d %H:%M"))

        # 해당 시간 ~ 1시간 구간
        start_of_hour = target
        end_of_hour = target + timedelta(hours=1)

        # 현재 시간대 공연
        current_slot_club = self.queryset.filter(
            type="club",
            start_time__lt=end_of_hour,
            end_time__gt=start_of_hour
        )

        # 이후 남은 공연
        remaining_club = self.queryset.filter(
            type="club",
            start_time__date=target.date(),
            start_time__gte=end_of_hour
        )

        # 연예인 공연 (그날 전체)
        celebrity_qs = self.queryset.filter(
            type="celebrity",
            start_time__date=target.date()
        )

        return Response({
            "day": day,
            "time": time,
            "club": {
                "current_slot": self.get_serializer(current_slot_club, many=True).data,
                "remaining": self.get_serializer(remaining_club, many=True).data,
            },
            "celebrity": self.get_serializer(celebrity_qs, many=True).data,
        })
