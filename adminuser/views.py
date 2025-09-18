from django.shortcuts import render

# Create your views here.
from .models import Admin

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings

from .services import issue_uid_by_code, invalidate_uid
from .permissions import IsAdminAuthenticated


class AdminLoginView(APIView): # 관리자 코드 검증 -> UID 방급
    # POST /admin/login
    # Body: {"admin_code": "999"}
    # 성공 시 UID, role, name 반환
    
    permission_classes = [permissions.AllowAny]  # 로그인은 공개 엔드포인트

    def post(self, request):
        code = (request.data or {}).get("admin_code", "")
        code = str(code).strip()

        if not code:
            return Response({"error": "admin_code is required"}, status=status.HTTP_400_BAD_REQUEST)

        uid, admin = issue_uid_by_code(code)
        if not uid:
            return Response({"error": "Invalid admin code"}, status=status.HTTP_401_UNAUTHORIZED)

        data = {
            "message": "로그인 성공",
            "uid": uid, # 프론트: localStorage.setItem("adminUID", uid)
            "role": admin.role, # Staff | Club | Major
            "name": admin.name, # ex) "컴퓨터공학과", "총학생회", "멋쟁이사자차러머"
            # "expires_in": getattr(settings, "ADMIN_UID_TTL", 3600),  # UX용 일단 비활성화
        }
        return Response(data, status=status.HTTP_200_OK)


class AdminMeView(APIView): # 인증 확인용 - IsAdminAuthenticated로 보호
    # GET /admin/me
    # 헤더 - Authorization: Bearer <UID>
    # 성공 시 현재 관리자 정보 반환
    
    permission_classes = [IsAdminAuthenticated]

    def get(self, request):
        admin = request.user_admin  # UIDAuthentication에서 가져옴
        return Response({
            "uid": request.admin_uid,
            "role": admin.role,
            "name": admin.name,
            "message": "유효한 관리자입니다"
        }, status=status.HTTP_200_OK)


class AdminLogoutView(APIView): # 개발 테스트에서 필요한 로그아웃 기능. UID 무효화(캐시 삭제) -> 이후 요청 401 응답
    # POST /admin/logout
    # 헤더 - Authorization: Bearer <UID>
    # 서버 캐시에서 UID 제거 -> 이후 요청은 401
    
    permission_classes = [IsAdminAuthenticated]

    def post(self, request):
        invalidate_uid(request.admin_uid)
        return Response({"message": "관리자 로그아웃 되었습니다"}, status=status.HTTP_200_OK)
