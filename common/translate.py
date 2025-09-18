import os
import time
from typing import Dict, Optional

from google.cloud import translate
from google.api_core.retry import Retry

def call_google_translate(
    source_lang: Optional[str],
    target_lang: str,
    text: str,
) -> Dict:
    """
    Google Cloud Translation v3 – 단일 텍스트 번역
    - source_lang: "ko", "en", "ja", "zh-CN" 등. 빈 문자열/None이면 자동 감지.
    - target_lang: 필수. "en", "ja", "zh-CN" 등.
    - GOOGLE_APPLICATION_CREDENTIALS: 서비스계정 JSON 경로(환경변수/ .env)
    - GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_LOCATION: 프로젝트/리전(기본 global)
    """
    t0 = time.time()

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    if not project_id:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT is not set")

    client = translate.TranslationServiceClient()
    parent = f"projects/{project_id}/locations/{location}"

    request = {
        "parent": parent,
        "contents": [text],
        "target_language_code": target_lang,
        "mime_type": "text/plain",
    }
    # source_lang이 비어있으면(자동감지 원할 때) 넣지 않는다.
    if source_lang:
        request["source_language_code"] = source_lang

    response = client.translate_text(
        request=request,
        retry=Retry(deadline=10.0),  # 총 재시도 제한시간
        timeout=8.0,                 # 단일 요청 타임아웃
    )
    translations = response.translations
    translated_text = translations[0].translated_text if translations else ""

    return {
        "translated_text": translated_text,
        "provider_latency_ms": int((time.time() - t0) * 1000),
    }
