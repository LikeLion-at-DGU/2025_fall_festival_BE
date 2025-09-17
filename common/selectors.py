import os
from django.core.cache import cache
from .models import Translation

CACHE_TTL = int(os.getenv("TRANSLATION_CACHE_TTL_SEC", "86400"))

def _key(entity_type, entity_id, field, target_lang, checksum):
    return f"translation:{entity_type}:{entity_id}:{field}:{target_lang}:{checksum}"

def get_translation(entity_type, entity_id, field, target_lang, checksum):
    key = _key(entity_type, entity_id, field, target_lang, checksum)
    hit = cache.get(key)
    if hit:
        return hit

    try:
        obj = Translation.objects.get(
            entity_type=entity_type,
            entity_id=entity_id,
            field=field,
            target_lang=target_lang,
            status="ok",
            checksum=checksum,
        )
        data = {
            "translated_text": obj.translated_text,
            "status": obj.status,
            "provider": obj.provider,
            "meta": obj.meta,
        }
        cache.set(key, data, CACHE_TTL)
        return data
    except Translation.DoesNotExist:
        return None
