from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from .models import *
from .serializers import *
from .services import *
from .selectors import *
import random

class BoothViewSet(viewsets.ModelViewSet):
    
    def get_serializer_class(self):
        if self.action == "list":
            return BoothListSerializer
        
        return BoothListSerializer
    
    def get_queryset(self):
        queryset = Booth.objects.all()
        keyword = self.request.query_params.get("keyword")
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) |
                Q(admin__name__icontains = keyword)
            )
        return queryset
    
    # 목록 조회 (GET /booths?keyword=사자)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={"request": request}) 
        return Response({"results": serializer.data})
    
    
    @action(detail=False, methods=["post"], url_path="list")
    def booth_list(self, request):
        """
        POST /booths/list/
        부스 목록 조회 (필터/정렬)
        """
        data = request.data

        date = data.get("date")
        types = data.get("types")
        building_id = data.get("building_id")
        user_location = data.get("user_location")
        ordering = data.get("ordering", "auto")
        top_liked_3 = data.get("top_liked_3", False)
        is_night = data.get("is_night")

        if user_location and not ("x" in user_location and "y" in user_location):
            return Response(
                {"error": "user_location must include x and y"},
                status=status.HTTP_400_BAD_REQUEST
            )

        booths = get_booth_list(
            date=date,
            types=types,
            building_id=building_id,
            user_location= user_location,
            ordering=ordering,
            top_liked_3=top_liked_3,
            is_night=is_night,
            is_event=data.get("is_event")
        )

        serializer = BoothListSerializer(booths, many=True, context={"request": request, "date": date})

        return Response({
            "results": serializer.data
        }, status=status.HTTP_200_OK)


    @action(detail=False, methods=["post"], url_path="nearby")
    def nearby_booths(self, request):
        """
        POST /booths/nearby/
        사용자 좌표 기반으로 가장 가까운 Location을 찾고,
        해당 Location의 Booth 중 랜덤 3개 반환
        """
        data = request.data
        user_location = data.get("user_location")
        is_night = data.get("is_night")
        if not user_location or "x" not in user_location or "y" not in user_location:
            return Response({"error": "user_location must include x, y"}, status=400)

        user_x = float(user_location["x"])
        user_y = float(user_location["y"])

        # 1) 모든 Location 거리순 정렬  # ← 여기 수정됨
        locations = list(Location.objects.all())
        locations_with_dist = []
        for loc in locations:
            if loc.latitude and loc.longitude:
                dist = calculate_distance(user_x, user_y, loc.latitude, loc.longitude)
                locations_with_dist.append((loc, dist))

        if not locations_with_dist:
            return Response({"error": "No valid locations"}, status=404)

        locations_with_dist.sort(key=lambda x: x[1])  # 거리 오름차순

        nearest_location = None
        min_dist = None
        booths = []

        # 2) 가까운 순서대로 탐색, Booth 있으면 break  # ← 여기 수정됨
        for loc, dist in locations_with_dist:
            qs = Booth.objects.filter(
                location=loc,
                category=Booth.Category.BOOTH
            )
            if isinstance(is_night, bool):
                qs = qs.filter(is_night=is_night)

            if qs.exists():
                nearest_location = loc
                min_dist = dist
                booths = list(qs)
                break

        if not booths:
            return Response({
                "nearest_location": None,
                "distance_m": None,
                "booths": []
            }, status=200)

        serializer = BoothListSerializer(
            booths,
            many=True,
            context={"request": request, "date": data.get("date")}
        )

        return Response({
            "nearest_location": nearest_location.name,
            "distance_m": int(round(min_dist)),
            "booths": serializer.data
        }, status=200)
    

    @action(detail=False, methods=["get"], url_path=r"detail/(?P<pk>\d+)")
    def booth_detail(self, request, pk=None): 
        """
        /booths/detail/{id}/ : 부스 상세
        """
        booth = get_object_or_404(Booth, id=pk)

        # 화장실 상세
        if booth.category == Booth.Category.TOILET:
            booth = get_toilet_detail(pk)
            serializer = ToiletDetailSerializer(booth, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 주류 상세
        elif booth.category == Booth.Category.DRINK:
            booth = get_drink_detail(pk)
            serializer = DrinkDetailSerializer(booth, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 푸드트럭 상세
        elif booth.category == Booth.Category.FOODTRUCK:
            booth = get_foodtruck_detail(pk)
            serializer = FoodtruckDetailSerializer(booth, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 주간부스 상세
        elif booth.category == Booth.Category.BOOTH and not booth.is_night:
            serializer = DayBoothDetailSerializer(booth, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 야간부스 상세
        elif booth.category == Booth.Category.BOOTH and booth.is_night:
            serializer = NightBoothDetailSerializer(booth, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "해당 카테고리를 지원하지 않습니다"}, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(
        ratelimit(key="ip", rate="5/h", method="POST", block=True)  # IP당 1시간 5회
    )
    
    ######################################################
    # 좋아요 기능
    
    @action(detail=True, methods=["post"], url_path="likes")
    def likes(self, request, pk=None):
        booth = get_object_or_404(Booth, id=pk)
        
        # 1. 현재 좋아요 개수 확인
        if booth.like_cnt >= 300:
            return Response(
                {"error": "좋아요가 300개를 초과하여 추가할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 프론트에서 보낸 user_id 확인 (첫 요청 시 null일 수 있음)
        user_id = request.data.get("user_id")
        
        # user_id가 없거나 빈 문자열이면 새로운 세션 키 생성
        if not user_id or user_id == "null" or user_id == "undefined":
            if not request.session.session_key:
                request.session.create()
            user_id = request.session.session_key
            print(f"새로운 user_id 생성: {user_id}")  # 디버깅용
        else:
            print(f"기존 user_id 사용: {user_id}")  # 디버깅용

        # 기존 좋아요 확인
        try:
            like = Like.objects.get(user_id=user_id, booth=booth)
            # 이미 좋아요가 존재하면 토글 (좋아요 <-> 좋아요 취소)

            like.is_liked = not like.is_liked
            like.save()

            if like.is_liked:
                message = "부스 좋아요"
                status_code = status.HTTP_200_OK
            else:
                message = "부스 좋아요 취소"
                status_code = status.HTTP_200_OK

        except Like.DoesNotExist:
            # 좋아요가 없으면 새로 생성
            Like.objects.create(user_id=user_id, booth=booth, is_liked=True)
            message = "부스 좋아요"
            status_code = status.HTTP_201_CREATED

        # 현재 좋아요 개수 계산 및 booth.like_cnt 업데이트
        likes_count = Like.objects.filter(booth=booth, is_liked=True).count()
        booth.like_cnt = likes_count
        booth.save()

        return Response({
            "message": message,
            "booth_id": booth.id,
            "likes_count": likes_count,
            "is_liked": Like.objects.filter(user_id=user_id, booth=booth, is_liked=True).exists(),
            "user_id": user_id
        }, status=status_code)

    # def _get_client_ip(self, request):
    #     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    #     if x_forwarded_for:
    #         ip = x_forwarded_for.split(',')[0].strip()
    #     else:
    #         ip = request.META.get('REMOTE_ADDR', '')
    #     return ip
    
    @action(detail=False, methods=["delete"], url_path="likes")
    def delete_like(self, request, pk=None):
        """
        DELETE /booths/likes/
        """
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"error": "user_id is required in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 해당 유저의 모든 Like 삭제
        deleted_count, _ = Like.objects.filter(user_id=user_id).delete()

        # 모든 Booth의 좋아요 개수 갱신
        booths = Booth.objects.all()
        for booth in booths:
            likes_count = Like.objects.filter(booth=booth, is_liked=True).count()
            booth.like_cnt = likes_count
            booth.save()

        return Response({
            "message": f"{deleted_count}개의 좋아요 삭제 완료",
            "user_id": user_id
        }, status=status.HTTP_200_OK)
        
    #########################################################
    
    
    @action(detail=False, methods=["post"], url_path="sync/start")
    def start_sync(self, request):
        """
        POST /booths/sync/start/
        부스 데이터 동기화 시작 (관리자 전용)
        """
        from .dorders import start_booth_sync
        
        try:
            success = start_booth_sync()
            if success:
                return Response({
                    "statusCode": 200,
                    "message": "부스 데이터 동기화가 시작되었습니다.",
                    "data": {}
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "statusCode": 400,
                    "message": "부스 데이터 동기화 시작에 실패했습니다.",
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "statusCode": 500,
                "message": f"동기화 시작 중 오류가 발생했습니다: {str(e)}",
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=["post"], url_path="sync/stop")
    def stop_sync(self, request):
        """
        POST /booths/sync/stop/
        부스 데이터 동기화 중지 (관리자 전용)
        """
        from .dorders import stop_booth_sync
        
        try:
            success = stop_booth_sync()
            if success:
                return Response({
                    "statusCode": 200,
                    "message": "부스 데이터 동기화가 중지되었습니다.",
                    "data": {}
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "statusCode": 400,
                    "message": "부스 데이터 동기화 중지에 실패했습니다.",
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "statusCode": 500,
                "message": f"동기화 중지 중 오류가 발생했습니다: {str(e)}",
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=["post"], url_path="sync/once")
    def sync_once(self, request):
        """
        POST /booths/sync/once/
        부스 데이터 한 번 동기화 (관리자 전용)
        """
        from .dorders import sync_booth_data_once
        
        try:
            success = sync_booth_data_once()
            if success:
                return Response({
                    "statusCode": 200,
                    "message": "부스 데이터 동기화가 완료되었습니다.",
                    "data": {}
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "statusCode": 400,
                    "message": "부스 데이터 동기화에 실패했습니다.",
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "statusCode": 500,
                "message": f"동기화 중 오류가 발생했습니다: {str(e)}",
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=["get"], url_path="sync/status")
    def sync_status(self, request):
        """
        GET /booths/sync/status/
        부스 데이터 동기화 상태 조회 (관리자 전용)
        """
        from .dorders import get_sync_status
        
        try:
            sync_status_data = get_sync_status()
            return Response({
                "statusCode": 200,
                "message": "동기화 상태 조회 성공",
                "data": sync_status_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "statusCode": 500,
                "message": f"동기화 상태 조회 중 오류가 발생했습니다: {str(e)}",
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
