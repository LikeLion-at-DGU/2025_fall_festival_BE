import hashlib
import time
from .models import Translation
from .translate import call_google_translate

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def create_or_update_translation(
    *,
    entity_type: str,
    entity_id: str,
    field: str,
    source_lang: str,
    target_lang: str,
    source_text: str,
    provider: str = "google",
) -> Translation:
    """
    - checksum으로 원문 변경 감지
    - translated_text/status/meta 갱신
    """
    checksum = _sha256(source_text)

    obj, _ = Translation.objects.get_or_create(
        entity_type=entity_type,
        entity_id=entity_id,
        field=field,
        target_lang=target_lang,
        defaults={
            "source_lang": source_lang,
            "source_text": source_text,
            "checksum": checksum,
            "status": "pending",
            "provider": provider,
        },
    )

    need_refresh = (obj.checksum != checksum) or (obj.status != "ok")
    if need_refresh:
        try:
            t0 = time.time()
            res = call_google_translate(
                source_lang if source_lang else None,
                target_lang,
                source_text,
            )
            latency = int((time.time() - t0) * 1000)

            obj.source_lang = source_lang
            obj.source_text = source_text
            obj.translated_text = res.get("translated_text", "")
            obj.checksum = checksum
            obj.status = "ok"
            obj.provider = provider
            obj.meta = {"provider_latency_ms": res.get("provider_latency_ms", latency)}
            obj.save()
        except Exception as e:
            obj.status = "error"
            obj.meta = {"error": str(e)}
            obj.save()

    return obj
