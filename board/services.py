from adminuser.models import Admin

def get_writer_from_uid(uid: str) -> str | None:
    """
    UID(code)로 Admin 조회 후 name 반환.
    유효하지 않으면 None 반환.
    """
    if not uid:
        return None
    try:
        admin = Admin.objects.get(code=uid)
        return admin.name
    except Admin.DoesNotExist:
        return None