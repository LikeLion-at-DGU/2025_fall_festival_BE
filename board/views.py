# API 입출력형태를 결정
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import *
from .serializers import *

# 총학 공지 등록
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all().order_by("-created_at")
    serializer_class = BoardPolymorphicSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    # def get_serializer_class(self):
    #     if self.action == "create":
    #         return BoardPolymorphicSerializer
    #     elif self.action in ["list", "retrieve"]:
    #         return BoardListSerializer
    #     return BoardPolymorphicSerializer

    

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     total_count = queryset.count()
    #     return Response({
    #         "message": "게시글 목록 조회에 성공하였습니다.", 
    #         "total_count": total_count,
    #         "board": serializer.data
    #     })

# 분실물 게시물 LOST Item 모델 추가
# post 생성 권한은 총학, 부스, admin에게만 있음
# admin/post 이렇게 할 필요가 있을까? 흠..


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all().order_by("-created_at")
    serializer_class = NoticeSerializer
    authentication_classes = []
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
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response(
            {"message": "분실물이 등록되었습니다.", "board_id": board.id, "board_title": board.title},
            status=status.HTTP_201_CREATED,
        )