from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import Booth
from .serializers import ToiletDetailSerializer
from .services import get_toilet_detail


class BoothDetailAPIView(APIView):
    permission_classes = [AllowAny] # 로그인 없이 접근 가능
    """
    /booths/detail/{id}/
    """

    def get(self, request, pk):
        booth = get_object_or_404(Booth, id=pk)

        if booth.category == Booth.Category.TOILET: # 부스 카테고리가 Toilet인 경우
            booth = get_toilet_detail(pk)
            serializer = ToiletDetailSerializer(booth)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "요청한 부스가 화장실 카테고리가 아님"}, status=status.HTTP_400_BAD_REQUEST)
