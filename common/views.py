from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
# 필요시 로컬 테스트만 열 때:
from rest_framework.permissions import AllowAny

from .serializers import TranslationSerializer
from .models import Translation
from .selectors import get_translation
from .services import create_or_update_translation, _sha256


class TranslationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Translation.objects.all().order_by("-updated_at")
    serializer_class = TranslationSerializer
    # 개발용(로컬 스모크 테스트)만 잠깐 열 때:
    permission_classes = [AllowAny]

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

        d = request.data
        req_checksum = _sha256(d["source_text"])

        # 1) 캐시/DB 히트 확인 (checksum 포함)
        hit = get_translation(
            d["entity_type"],
            d["entity_id"],
            d["field"],
            d["target_lang"],
            req_checksum,
        )
        if hit:
            return Response(hit, status=200)

        # 2) 생성/갱신
        obj = create_or_update_translation(
            entity_type=d["entity_type"],
            entity_id=d["entity_id"],
            field=d["field"],
            source_lang=d["source_lang"],
            target_lang=d["target_lang"],
            source_text=d["source_text"],
            provider=d.get("provider", "google"),
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

    @action(detail=False, methods=["post"], url_path="resolve-batch")
    def resolve_batch(self, request):
        """
        여러 번역 요청을 한 번에 처리
        target_lang: 필수
        items: [
        {
            "entity_type": "stage",
            "entity_id": "123",
            "fields": [
                {"field": "StageName", "source_lang": "ko", "source_text": "메인 밴드 공연"},
                {"field": "StageLocation", "source_lang": "ko", "source_text": "대강당"}
            ]
        },
        ...
        ]
        """
        target_lang = request.data.get("target_lang")
        items = request.data.get("items", [])

        if not target_lang:
            return Response({"detail": "Missing field: target_lang"}, status=400)

        results = []
        for item in items:
            entity_type = item["entity_type"]
            entity_id = item["entity_id"]
            for f in item["fields"]:
                field = f["field"]
                source_text = f["source_text"]
                source_lang = f.get("source_lang", "")
                checksum = _sha256(source_text)

                # 1) 캐시/DB 조회
                hit = get_translation(entity_type, entity_id, field, target_lang, checksum)
                if hit:
                    translated = hit
                else:
                    # 2) 새로 번역 생성
                    obj = create_or_update_translation(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        field=field,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        source_text=source_text,
                    )
                    translated = {
                        "translated_text": obj.translated_text,
                        "status": obj.status,
                        "provider": obj.provider,
                        "meta": obj.meta,
                    }

                results.append({
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "field": field,
                    "translated": translated,
                })

        return Response({"results": results}, status=200)
