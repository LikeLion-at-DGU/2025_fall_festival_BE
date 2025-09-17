# board/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

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
    
# 게시물 생성/수정/조회, 관련 게시물
# POST /board/notices 또는 losts
# PATCH, GET /board/{id}
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all().order_by("-created_at")
    serializer_class = BoardListSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return BoardListSerializer
        if self.action in ["retrieve", "update", "partial_update"]:
            if isinstance(self.get_object(), Lost):
                return LostSerializer
            elif isinstance(self.get_object(), Notice):
                return NoticeSerializer
        return BoardSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_count = queryset.count()
        return Response({
            "message": "게시글 목록 조회에 성공하였습니다.", 
            "total_count": total_count,
            "board": serializer.data
        })

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        # 긴급 공지 1건은 미리 DB에 등록해두고, id 프론트에 공유 필요
        if board.is_emergency == True:
            message = "긴급 공지가 성공적으로 수정되었습니다."
        else:
            message = "게시글이 수정되었습니다."

        return Response({
                "message": message,
                "board_id": board.id,
                "board_title": board.title,
        })
    
    # GET /board/{id}/related, 관련 게시물 조회
    @action(detail=True, methods=["GET"])
    def related(self, request, pk=None):
        instance = self.get_object()
        created_at = instance.created_at

        related = (
            Board.objects.filter(created_at__gt=created_at)
            .order_by("created_at")[:3]
        )

        serializer = BoardListSerializer(related, many=True)
        return Response({
            "message": "관련 게시글 조회에 성공하였습니다.",
            "related": serializer.data
        })
    
    @action(detail=False, methods=["GET", "PATCH"])
    def emergency(self, request):

        if request.method == "GET":
            emergency = Notice.objects.filter(is_emergency=True).order_by("created_at").first()
            if not emergency:
                return Response({"message": "긴급 공지가 없습니다."}, status=404)
            serializer = NoticeSerializer(emergency)
            return Response({"message": "긴급 공지 조회에 성공하였습니다.", "notice": serializer.data})

class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all().order_by("-created_at")
    serializer_class = NoticeSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response(
            {"message": "공지 작성이 완료되었습니다.", "board_id": board.id},
            status=status.HTTP_201_CREATED,
        )
    
    
    
# Lost 전용 CRUD
class LostViewSet(viewsets.ModelViewSet):
    queryset = Lost.objects.all().order_by("-created_at")
    serializer_class = LostSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response(
            {"message": "분실물이 등록되었습니다.", "board_id": board.id, "board_title": board.title},
            status=status.HTTP_201_CREATED,
        )
    

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