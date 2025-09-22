from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class BoothConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booth'
    
    def ready(self):
        """
        Django 앱이 준비되었을 때 실행되는 메서드
        부스 데이터 자동 동기화를 시작합니다.
        """
        try:
            from .dorders import auto_start_sync
            auto_start_sync()
        except Exception as e:
            logger.error(f"Booth 앱 시작 시 자동 동기화 설정 중 오류: {str(e)}")
