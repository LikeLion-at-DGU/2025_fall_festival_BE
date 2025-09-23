#이벤트 시간 끝나면 is_event = false로 바꾸기

from celery import shared_task
from django.utils import timezone
from .models import BoothEvent
from booth.models import Booth

@shared_task
def update_booth_event_status():
    now = timezone.now()
    # 모든 부스 이벤트 확인
    events = BoothEvent.objects.select_related("booth").all()
    for event in events:
        booth = event.booth

        # 현재 이벤트가 진행 중인지 확인
        if event.start_time <= now < event.end_time:
            if not booth.is_event:  # 상태 변경 필요할 때만 저장
                booth.is_event = True
                booth.save(update_fields=["is_event"])
        else:
            if booth.is_event:
                # 단, 다른 진행 중인 이벤트가 있는지 확인
                overlapping = BoothEvent.objects.filter(
                    booth=booth,
                    start_time__lte=now,
                    end_time__gt=now
                ).exists()
                if not overlapping:
                    booth.is_event = False
                    booth.save(update_fields=["is_event"])
               
