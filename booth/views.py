from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import Booth
from .selectors import get_booth_list
from .serializers import ToiletDetailSerializer, DrinkDetailSerializer, BoothListSerializer
from .services import get_toilet_detail, get_drink_detail

class BoothViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="list")
    def booth_list(self, request):
        """
        POST /booths/list/
        부스 목록 조회 (필터/정렬/페이징)
        """
        data = request.data

        date = data.get("date")
        types = data.get("types")
        building_id = data.get("building_id")
        user_location = data.get("user_location")
        has_event_history = data.get("has_event", False)
        ordering = data.get("ordering", "auto")
        top_liked_3 = data.get("top_liked_3", False)

        booths = get_booth_list(
            date=date,
            types=types,
            building_id=building_id,
            user_location=user_location,
            has_event_history=has_event_history,
            ordering=ordering,
            top_liked_3=top_liked_3
        )

        serializer = BoothListSerializer(booths, many=True)

        return Response({
            "results": serializer.data
        }, status=status.HTTP_200_OK)
    

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

        return Response({"error": "해당 카테고리를 지원하지 않습니다"}, status=status.HTTP_400_BAD_REQUEST)


