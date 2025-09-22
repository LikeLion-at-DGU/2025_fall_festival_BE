# 토큰 만료 시간 필드 보고 자동 삭제 기능

from celery import shared_task
from django.utils import timezone
from .models import AdminUID

@shared_task
def delete_expired_admin_uids():
    now = timezone.now()
    expired_qs = AdminUID.objects.filter(uid_expires_at__lt=now)
    count = expired_qs.count()
    expired_qs.delete()
    return f"{count} expired AdminUID(s) deleted."
