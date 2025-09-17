# board/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .models import *
from .serializers import *

# uid 가 request 로 오고 admin의 code에 저장
# 간단 토큰 저장소 (실제 배포시 DB나 Redis 사용)
TOKEN_STORE = {
    "A1B2C3D4": 1,  # token: admin_id
    "B2C3D4E5": 2,
}


def get_admin_from_token(request):
    token = request.headers.get('Authorization')
    if not token or token not in TOKEN_STORE:
        return None
    from adminuser.models import Admin
    try:
        return Admin.objects.get(id=TOKEN_STORE[token])
    except Admin.DoesNotExist:
        return None

class BoothEventViewSet(viewsets.ModelViewSet):
    queryset = BoothEvent.objects.all()
    serializer_class = BoothEventSerializer

    # POST /board/events/
    def create(self, request, *args, **kwargs):
        # 1. 토큰으로 admin 확인
        admin = get_admin_from_token(request)
        if not admin:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. role 체크 (동아리, 학과만 허용)
        if admin.role not in ['Club', '동아리','Major', '학과']:
            return Response({"error": "권한이 없습니다. 동아리/학과 관리자만 이벤트 생성 가능"}, 
                            status=status.HTTP_403_FORBIDDEN)

        
        # 3. admin 소속 Booth 가져오기
        try:
            booth = Booth.objects.get(admin=admin)
        except Booth.DoesNotExist:
            return Response({"error": "관리자 소속 부스가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. 이벤트 생성
        booth_event = BoothEvent.objects.create(
            booth=booth,
            title=request.data.get('title'),
            detail=request.data.get('detail'),
            start_time=request.data.get('start_time'),
            end_time=request.data.get('end_time')
        )

        serializer = self.get_serializer(booth_event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)