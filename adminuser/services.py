from django.conf import settings
from django.core.cache import cache
from .models import Admin, AdminUID
import secrets
import string

from django.utils import timezone
from datetime import timedelta

# UID에 사용할 문자 집합 (A~Z + 숫자 0~9)
_UID_CHARS = string.ascii_uppercase + string.digits

def _generate_uid(length: int = 8) -> str:
    # UID(랜덤 8자리 문자열) 생성. ex: "7F9K2D1A"
    return "".join(secrets.choice(_UID_CHARS) for _ in range(length))

CACHE_KEY_PREFIX = "admin_uid:"  # CACHE_KEY에 prefix를 붙여 충돌 방지


def issue_uid_by_code(admin_code: str):
    
    # 입력받은 관리자 코드가 Admin 테이블에 존재하는지 확인
    try:
        admin = Admin.objects.get(code=admin_code)
    except Admin.DoesNotExist:
        return None, None

    # 이미 발급된 UID 삭제 (같은 admin_id 기준)
    AdminUID.objects.filter(admin=admin).delete()
    
    # 유효하면 UID를 새로 생성
    uid = _generate_uid(8)

    # 캐시에 UID->admin.id 매핑을 30초.. 동안 저장
    ttl = getattr(settings, "ADMIN_UID_TTL", 30)  # 기본 만료시간 = 1시간, 3600
    cache.set(f"{CACHE_KEY_PREFIX}{uid}", admin.id, ttl)

    # DB에 UID와 만료시간 저장
    expires_at = timezone.now() + timedelta(seconds=ttl)
    AdminUID.objects.create(admin=admin, uid=uid, uid_expires_at=expires_at)

    return uid, admin # (uid, admin) 튜플 반환


def resolve_admin_by_uid(uid: str): # UID로부터 연결된 Admin 객체

    if not uid:
        return None

    # #  캐시에서 admin_id 가져옴
    # admin_id = cache.get(f"{CACHE_KEY_PREFIX}{uid}")

    # # admin_id 가 존재하면 Admin 객체, 없으면 None 반환
    # # if not admin_id:
    # #     return None

    # if admin_id:
    #     try:
    #         return Admin.objects.get(id=admin_id)
    #     except Admin.DoesNotExist:
    #         return None
    
    # DB에 UID가 있는지 체크, 만료시간 체크
    try:
        admin_uid = AdminUID.objects.get(uid=uid)
        if admin_uid.uid_expires_at and admin_uid.uid_expires_at > timezone.now():
            return admin_uid.admin
    except AdminUID.DoesNotExist:
        return None
    return None


def invalidate_uid(uid: str):
    # UID를 캐시에서 삭제 -> 강제 로그아웃
    cache.delete(f"{CACHE_KEY_PREFIX}{uid}")
    AdminUID.objects.filter(uid=uid).delete()