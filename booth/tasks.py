from celery import shared_task
from .dorders import sync_booth_data_once
import logging

logger = logging.getLogger(__name__)

@shared_task
def sync_booth_data_task():
    logger.info("부스 데이터 동기화 태스크 실행")
    return sync_booth_data_once()