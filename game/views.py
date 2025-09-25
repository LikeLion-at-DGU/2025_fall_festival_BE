from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from .models import Game, Coupon
from .serializers import GameSerializer
from booth.models import Booth
from django.db import transaction

class GameViewset(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @method_decorator(
        ratelimit(key="ip", rate="10/h", method="POST", block=True)
    )
    @action(detail=False, methods=['post'], url_name='start', url_path='start')
    def start(self, request):
        user_id = request.data.get("user_id")

        # user_id 없으면 세션 키 발급
        if not user_id or user_id == "none":
            if not request.session.session_key:
                request.session.create()
            user_id = request.session.session_key

        # 마지막 게임 조회
        last_game = Game.objects.filter(user_id=user_id).order_by('-try_times').first()
        next_try = last_game.try_times + 1 if last_game else 1

        if next_try > 5:
            return Response({"message": "5회 시도를 모두 완료했습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 다음 시도 게임 생성
        game = Game.objects.create(user_id=user_id, try_times=next_try, is_started=True)

        serializer = self.get_serializer(game)
        return Response({
            "message": "게임이 시작되었습니다.",
            "data": {
                "user_id": user_id,
                "try_times": game.try_times
            }
        }, status=status.HTTP_200_OK)
    
    @method_decorator(
        ratelimit(key="ip", rate="15/h", method="POST", block=True)
    )
    @action(detail=False, methods=['post'], url_name='success', url_path='success')
    def success(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"message": "user_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 진행 중인 게임 조회
        game = Game.objects.filter(user_id=user_id, is_started=True).order_by('-try_times').first()
        if not game:
            return Response({"message": "진행 중인 게임이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 게임 종료 처리
        game.is_started = False
        game.is_end = True
        game.save()

        # 전체 성공 게임 수 확인 (현재 게임 포함)
        total_success_count = Game.objects.filter(is_end=True).count()

        # 쿠폰 당첨 순번
        WINNING_NUMBERS = [30+11367, 43+11367, 72+11367, 81+11367, 100+11367, 111+11367, 189+11367, 211+11367, 240+11367, 256+11367, 299+11367, 312+11367, 333+11367, 357+11367, 411+11367, 444+11367, 478+11367, 512+11367, 560+11367, 600+11367]
        is_winner = total_success_count in WINNING_NUMBERS

        return Response({
            "message": "쿠폰 당첨" if is_winner else "쿠폰 미당첨",
            "data": {
                "is_coupon": is_winner            
            }
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_name='coupon', url_path='coupon')
    def coupon(self, request):
        user_id = request.data.get("user_id")
        booth_name = request.data.get("booth_name")

        if not user_id or not booth_name:
            return Response({"message": "user_id와 booth_name이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 마지막 종료된 게임 조회
        game = Game.objects.filter(user_id=user_id, is_started=False).order_by('-try_times').first()
        if not game:
            return Response({"message": "게임이 종료되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)
        if game.coupon:
            return Response({"message": "이미 쿠폰을 받으셨습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 부스의 미사용 쿠폰 중 ID 작은 순서대로 하나 가져와 원자적으로 is_used를 갱신
        with transaction.atomic():
            coupon_obj = Coupon.objects.filter(booth=booth_name, is_used=False).order_by('id').first()
            if not coupon_obj:
                return Response({"message": "해당 부스의 사용 가능한 쿠폰이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # DB 레벨에서 is_used를 원자적으로 업데이트. 다른 요청과의 경쟁을 피함.
            updated = Coupon.objects.filter(id=coupon_obj.id, is_used=False).update(is_used=True)
            if updated == 0:
                # 다른 트랜잭션이 이미 사용 처리했을 수 있음
                return Response({"message": "해당 부스의 사용 가능한 쿠폰이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            # 게임에 쿠폰 연결
            game.coupon = coupon_obj
            game.save()

            # 객체 인스턴스에 반영
            coupon_obj.is_used = True

        return Response({
            "message": "쿠폰이 발급되었습니다.",
            "data": {
                "coupon_id": coupon_obj.id,
                "coupon_code": coupon_obj.serial_code,
                "coupon_is_used": coupon_obj.is_used,
                "booth_name": booth_name
            }
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_name='successcount', url_path='successcount')
    def successcount(self, request):
        # 전체 성공 게임 수 확인
        total_success_count = Game.objects.filter(is_end=True).count()

        return Response({
            "message": "전체 성공 게임 수 조회 성공",
            "data": {
                "total_success_count": total_success_count
            }
        }, status=status.HTTP_200_OK)