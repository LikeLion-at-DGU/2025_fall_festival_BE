from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

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
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
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

        serializer = BoothListSerializer(booths, many=True, context={"date": date})

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

        # 1) 가장 가까운 Location 찾기
        locations = list(Location.objects.all())
        nearest_location = None
        min_dist = float("inf")

        for loc in locations:
            if loc.latitude and loc.longitude:
                dist = calculate_distance(user_x, user_y, loc.latitude, loc.longitude)
                if dist < min_dist:
                    min_dist = dist
                    nearest_location = loc

        if not nearest_location:
            return Response({"error": "No valid locations"}, status=404)

        # 2) 해당 location의 booth 조회
        booths = list(Booth.objects.filter(location=nearest_location))

        if isinstance(is_night, bool):
            booths = booths.filter(is_night=is_night)

        # 3) 랜덤 3개 선택
        if len(booths) > 3:
            booths = random.sample(booths, 3)

        serializer = BoothListSerializer(booths, many=True, context={"date": data.get("date")})

        return Response({
            "nearest_location": nearest_location.name,
            "distance_m": int(round(min_dist)),
            "booths": serializer.data
        }, status=200)
    

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

        # 1) 가장 가까운 Location 찾기
        locations = list(Location.objects.all())
        nearest_location = None
        min_dist = float("inf")

        for loc in locations:
            if loc.latitude and loc.longitude:
                dist = calculate_distance(user_x, user_y, loc.latitude, loc.longitude)
                if dist < min_dist:
                    min_dist = dist
                    nearest_location = loc

        if not nearest_location:
            return Response({"error": "No valid locations"}, status=404)

        # 2) 해당 location의 booth 조회
        booths = list(Booth.objects.filter(location=nearest_location))

        if isinstance(is_night, bool):
            booths = booths.filter(is_night=is_night)

        # 3) 랜덤 3개 선택
        if len(booths) > 3:
            booths = random.sample(booths, 3)

        serializer = BoothListSerializer(booths, many=True, context={"date": data.get("date")})

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
            serializer = ToiletDetailSerializer(booth)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 주류 상세
        elif booth.category == Booth.Category.DRINK:
            booth = get_drink_detail(pk)
            serializer = DrinkDetailSerializer(booth)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 푸드트럭 상세
        elif booth.category == Booth.Category.FOODTRUCK:
            booth = get_foodtruck_detail(pk)
            serializer = FoodtruckDetailSerializer(booth)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 주간부스 상세
        elif booth.category == Booth.Category.BOOTH and not booth.is_night:
            serializer = DayBoothDetailSerializer(booth)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 야간부스 상세
        elif booth.category == Booth.Category.BOOTH and booth.is_night:
            serializer = NightBoothDetailSerializer(booth)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "해당 카테고리를 지원하지 않습니다"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["get"], url_path="anonymous-like-status")
    def anonymous_like_status(self, request, pk=None):
        booth = get_object_or_404(Booth, id=pk)
        
        # 세션 키가 있는 경우에만 좋아요 상태 확인
        session_key = request.session.session_key
        is_liked = False
        
        if session_key:
            client_ip = self._get_client_ip(request)
            user_identifier = abs(hash(f"{session_key}_{client_ip}"))
            is_liked = Like.objects.filter(user_id=user_identifier, booth=booth, is_liked=True).exists()
        
        # 전체 좋아요 개수
        likes_count = Like.objects.filter(booth=booth, is_liked=True).count()
        
        return Response({
            "booth_id": booth.id,
            "likes_count": likes_count,
            "is_liked": is_liked
        }, status=status.HTTP_200_OK)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
