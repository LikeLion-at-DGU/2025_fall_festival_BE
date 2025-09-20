from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import *
from .serializers import *
from .services import *
from .selectors import *
import random

class gameViewset(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    
    @action(detail=True, methods=['post'], url_name='start', url_path='start')
    def start(self, request, pk=None):
        user_id = request.data.get("user_id")
        
        # user_id가 없으면 새로운 세션 키 생성
        if not user_id:
            if not request.session.session_key:
                request.session.create()
            user_id = request.session.session_key

        # 기존 좋아요 확인
        try:
            try_times = request.data.get("try_times", 0)
            if try_times >= 3:
                return Response({"message": "시도 횟수를 초과했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                game = Game.objects.create(user_id=user_id, is_started=True, try_times=try_times+1)
                serializer = self.get_serializer(game)
                return Response({
                    "message": "게임이 시작되었습니다.",
                    "data": {
                        "try_times": try_times + 1
                    }
                }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='end', url_path='end')
    def end(self, request, pk=None):
        game = self.get_object()
        if not game.is_started:
            return Response({"message": "게임이 시작되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        game.is_started = False
        game.save()
        return Response({"message": "게임이 종료되었습니다."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_name='success', url_path='success')
    def success(self, request, pk=None):
        game = self.get_object()
        if game.is_success:
            return Response({"message": "이미 성공한 게임입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 성공 시 일정 확률로 쿠폰 당첨
        success_chance = 0.5
        boothlist = ["멋쟁이사자처럼", "프론티어", "공대"]
        
        if random.random() < success_chance:
            game.is_success = True
            game.save()
            return Response({
                "message": "쿠폰 당첨",
                "data": {
                    'coupon_booth': boothlist
                }
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({"message": "쿠폰 미당첨"}, status=status.HTTP_200_OK)
    
    