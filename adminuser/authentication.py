from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .services import resolve_admin_by_uid

class UIDAuthentication(BaseAuthentication):
    
    # Authorization: Bearer <UID> 형태의 헤더를 해석해 관리자 인증 수행
    # 인증 성공 시 (user, auth) 튜플을 반환하며, 뷰에서 편하게 사용하도록 request.user_admin, request.admin_uid를 주입
    
    # AuthorizationL Bearer <UID> 형식을 구분하기 위한 키워드
    keyword = "Bearer"
    
    def authenticate(self, request):
        
        # Authorization 헤더 획득
        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            
            # 인증 시도 자체가 없으면 DRF가 다른 인증으로 넘기거나
            # permission 처리는 뷰, 설정에 맡긴다
            return None

        # Bearer <UID> 형태 헤더 해석
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0] != self.keyword:
            # 헤더 형식이 이상하면 인증 시도 없음으로 처리
            return None

        uid = parts[1].strip()
        if not uid:
            # UID가 비어있으면 인증 실패
            raise exceptions.AuthenticationFailed("관리자 로그아웃 되었습니다")

        # UID -> Admin 조회(만료/무효 시 None return)
        admin = resolve_admin_by_uid(uid)
        if not admin:
            # stale time 만료, 잘못된 UID, 강제 로그아웃 등의 상황
            raise exceptions.AuthenticationFailed("관리자 로그아웃 되었습니다")

        # DRF 규약에 따라 (user, auth) 튜플 반환
        # 우리는 관리자 개체만 필요하므로 user=admin, auth=uid를 사용
        # 추가로 뷰에서 편하도록 request에 주입
        request.user_admin = admin # Admin 인스턴스
        request.admin_uid = uid
        return (admin, uid)