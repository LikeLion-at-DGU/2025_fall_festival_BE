from rest_framework.permissions import BasePermission

class IsAdminAuthenticated(BasePermission):
    
    #UIDAuthentication이 성공해 request.user_admin이 채워진 경우에만 통과
    # 관리자 전용 엔드포인트 보호
    
    message = "관리자 인증이 필요합니다."

    def has_permission(self, request, view):
        return hasattr(request, "user_admin") and request.user_admin is not None
