from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
# 필요시 로컬 테스트만 열 때:
# from rest_framework.permissions import AllowAny

from .serializers import TranslationSerializer
from .models import Translation
from .selectors import get_translation
from .services import create_or_update_translation

class TranslationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Translation.objects.all().order_by("-updated_at")
    serializer_class = TranslationSerializer
    # 개발용(로컬 스모크 테스트)만 잠깐 열 때:
    # permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="resolve")
    def resolve(self, request):
        required = [
            "entity_type",
            "entity_id",
            "field",
            "source_lang",
            "target_lang",
            "source_text",
        ]
        for r in required:
            if r not in request.data:
                return Response({"detail": f"Missing field: {r}"}, status=400)

        data = request.data

        # 1) 캐시/DB 히트 확인
        hit = get_translation(
            data["entity_type"],
            data["entity_id"],
            data["field"],
            data["target_lang"],
        )
        if hit:
            return Response(hit, status=200)

        # 2) 생성/갱신
        obj = create_or_update_translation(
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            field=data["field"],
            source_lang=data["source_lang"],
            target_lang=data["target_lang"],
            source_text=data["source_text"],
            provider=data.get("provider", "google"),
        )
        if obj.status == "ok":
            return Response(
                {
                    "translated_text": obj.translated_text,
                    "status": obj.status,
                    "provider": obj.provider,
                    "meta": obj.meta,
                },
                status=200,
            )
        elif obj.status == "pending":
            return Response({"detail": "translation pending"}, status=202)
        else:
            return Response(
                {"detail": "translation error", "meta": obj.meta}, status=502
            )
