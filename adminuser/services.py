from django.conf import settings
from django.core.cache import cache
from .models import Admin
import secrets
import string

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

    # 유효하면 UID를 새로 생성
    uid = _generate_uid(8)

    # 캐시에 UID->admin.id 매핑을 1시간 동안 저장
    ttl = getattr(settings, "ADMIN_UID_TTL", 3600)  # 기본 만료시간 = 1시간
    cache.set(f"{CACHE_KEY_PREFIX}{uid}", admin.id, ttl)
    return uid, admin # (uid, admin) 튜플 반환


def resolve_admin_by_uid(uid: str): # UID로부터 연결된 Admin 객체
    #  캐시에서 admin_id 가져옴
    admin_id = cache.get(f"{CACHE_KEY_PREFIX}{uid}")

    # admin_id 가 존재하면 Admin 객체, 없으면 None 반환
    if not admin_id:
        return None
    try:
        return Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        return None


def invalidate_uid(uid: str):
    # UID를 캐시에서 삭제 -> 강제 로그아웃
    cache.delete(f"{CACHE_KEY_PREFIX}{uid}")