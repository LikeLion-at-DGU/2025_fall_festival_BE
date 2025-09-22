# board/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from .models import *
from .serializers import *
from adminuser.services import resolve_admin_by_uid


# 게시물 생성/수정/조회, 관련 게시물
# POST /board/notices 또는 losts
# PATCH, GET /board/{id}
class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Board.objects.all().order_by("-created_at")
    serializer_class = BoardPolymorphicSerializer

    def get_queryset(self):
        admin = getattr(self.request, "user_admin", None)

        if not admin:
            return Board.objects.all().order_by("-created_at")

        # 본인 글만 보이도록
        qs = Board.objects.filter(writer=admin.name)

        notice_ids = Notice.objects.filter(is_emergency=True).values_list("id", flat=True)
        qs = qs.exclude(id__in=notice_ids)

        return qs.order_by("-created_at")



    def get_serializer_class(self):
        if self.action == "list":
            # 리스트 조회용
            return BoardListSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            obj = self.get_object()
            if isinstance(obj, Lost):
                return LostSerializer
            elif isinstance(obj, Notice):
                return NoticeSerializer
            elif isinstance(obj, BoothEvent):
                return BoothEventSerializer
        return BoardPolymorphicSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_count = queryset.count()
        return Response({
            "message": "게시글 목록 조회에 성공하였습니다.", 
            "total_count": total_count,
            "result": serializer.data
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
                "board_content": board.content,
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        board_id = instance.id
        instance.delete()
        return Response(
            {
                "message": "게시글이 삭제되었습니다.",
                "board_id": board_id,
            },
            status=status.HTTP_200_OK,
        )
    
    # GET /board/{id}/related, 관련 게시물 조회
    @action(detail=True, methods=["GET"])
    def related(self, request, pk=None):
        instance = self.get_object()
        created_at = instance.created_at

        related = (
            Board.objects.filter(created_at__lt=created_at)
            .order_by("-created_at")[:3]
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
        uid = request.data.get("uid")
        admin = resolve_admin_by_uid(uid)
        if not admin:  
            return Response(
                {"message": "만료된 UID 입니다.",
                "uid_valid": False},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(writer=admin.name)

        return Response(
            {"message": "공지 작성이 완료되었습니다.", 
                "board_id": board.id,
                "writer": board.writer},
            status=status.HTTP_201_CREATED,
        )
    
# Lost 전용 CRUD
class LostViewSet(viewsets.ModelViewSet):
    queryset = Lost.objects.all().order_by("-created_at")
    serializer_class = LostSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        uid = request.data.get("uid")
        admin = resolve_admin_by_uid(uid)
        if not admin:  
            return Response(
                {"message": "만료된 UID 입니다.",
                    "uid_valid": False},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(writer=admin.name)

        return Response(
            {"message": "분실물이 등록되었습니다.", 
                "board_id": board.id, 
                "writer": board.writer,
                "board_title": board.title
                },
            status=status.HTTP_201_CREATED,
        )
    

class BoothEventViewSet(viewsets.ModelViewSet):
    queryset = BoothEvent.objects.all()
    serializer_class = BoothEventSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        total_count = queryset.count()
        return Response({
            "message": "이벤트 게시글 목록 조회에 성공하였습니다.", 
            "total_count": total_count,
            "result": serializer.data
        })
    
    # POST /board/events/
    def create(self, request, *args, **kwargs):
        uid = request.data.get("uid")  # 글 작성 시 전달되는 token/UID
        admin = resolve_admin_by_uid(uid)
        if not admin:  
            return Response(
                {"message": "만료된 UID 입니다.", "uid_valid": False},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Admin과 연결된 Booth 가져오기
        try:
            booth = Booth.objects.get(admin=admin)
        except Booth.DoesNotExist:
            return Response(
                {"message": "해당 관리자에게 연결된 부스가 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # 3. 데이터 유효성 검사 및 오류 처리 (Serializer 활용)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. 부스 이벤트 생성
        booth_event = BoothEvent.objects.create(
            booth=booth,
            writer=admin.name,
            title=request.data.get('title'),
            detail=request.data.get('detail'),
            start_time=request.data.get('start_time'),
            end_time=request.data.get('end_time')
        )
        
        # 5. 현재 시간이 start_time~end_time 안에 있는지 검사
        now = timezone.now()
        if booth_event.start_time <= now < booth_event.end_time:
            booth.is_event = True
        else:
            booth.is_event = False
        booth.save()

        serializer = self.get_serializer(booth_event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response({
            "message": "BoothEvent가 수정되었습니다.",
            "board_id": board.id,
            "writer": board.writer,
            "board_title": board.title
        })