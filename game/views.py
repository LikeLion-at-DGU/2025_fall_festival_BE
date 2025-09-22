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
    
    @action(detail=False, methods=['post'], url_name='start', url_path='start')
    def start(self, request, pk=None):
        user_id = request.data.get("user_id")
        
        # user_id가 없거나 "none"이면 새로 발급
        if not user_id or user_id == "none":
            if not request.session.session_key:
                request.session.create()
            user_id = request.session.session_key
            is_new_user = True
        else:
            is_new_user = False

        # 기존 게임 조회
        game = Game.objects.filter(user_id=user_id).first()
        
        # 게임 기록이 이미 있으면
        if game:
            if game.try_times >= 3:
                return Response({"message": "시도 횟수를 초과했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            game.try_times += 1
            game.is_started = True
            game.save()
        else:
            # 최초 게임 생성
            game = Game.objects.create(user_id=user_id, try_times=1, is_started=True)

        serializer = self.get_serializer(game)
        return Response({
            "message": "게임이 시작되었습니다.",
            "data": {
                "user_id": user_id,         # 프론트에 저장용
                "try_times": game.try_times
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

    @action(detail=False, methods=['post'], url_name='success', url_path='success')
    def success(self, request, pk=None):
        user_id = request.data.get("user_id")
        
        if not user_id:
            return Response({"message": "user_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # user_id로 가장 최근 게임 찾기
        game = Game.objects.filter(user_id=user_id).order_by('-id').first()
        
        if not game:
            return Response({"message": "게임을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # 게임이 이미 종료되었는지 확인
        if game.is_end:
            return Response({"message": "이미 종료된 게임입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 성공 시 일정 확률로 쿠폰 당첨
        success_chance = 0.5
        boothlist = ["멋쟁이사자처럼", "프론티어", "공대"]
        
        if random.random() < success_chance:
            # 게임 종료 처리
            game.is_end = True
            game.save()
            return Response({
                "message": "쿠폰 당첨",
                "data": {
                    'coupon_booth': boothlist
                }
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({"message": "쿠폰 미당첨"}, status=status.HTTP_200_OK)
    
    