"""
부스 정보 전체 조회 API 데이터 동기화 모듈
5분마다 부스 정보를 API로 조회하여 DB에 동기화합니다.
"""

import requests
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from django.db import transaction
from django.conf import settings
from django.utils import timezone

from .models import Booth, BoothDetail, Menu
from board.models import BoothEvent


# 로깅 설정
logger = logging.getLogger(__name__)

# 부스 데이터 동기화
class BoothDataSynchronizer:    
    def check_event(self):
        # 이벤트 글을 확인해 현재 이벤트 진행 시간인 부스 is_event True로 변경
        # 반대의 경우 false로 변경
        
        now = timezone.now()
        events = BoothEvent.objects.filter(start_date__lte=now, end_date__gte=now)
        event_booth_ids = events.values_list('booth_id', flat=True).distinct()

        Booth.objects.filter(id__in=event_booth_ids).update(is_event=True)
        Booth.objects.exclude(id__in=event_booth_ids).update(is_event=False)
    
    def __init__(self, api_url: str = None, api_headers: Dict = None): # 초기화
        self.api_url = api_url or "https://api.test-d-order.store/api/v2/public/d-order/booths/"
        self.api_headers = api_headers or {
            "Content-Type": "application/json",
            # "Authorization": "Bearer your-token-here"  # 필요시 추가
        }
        self.sync_interval = 300  # 5분 (300초)
        self.is_running = False
        self.sync_thread = None
    
    def fetch_booth_data(self) -> Optional[Dict]:
        """
        API에서 부스 데이터를 가져옵니다.
        
        Returns:
            Dict: API 응답 데이터 또는 None (실패시)
        """
        try:
            logger.info("부스 데이터 API 호출 시작")
            
            check_event = self.check_event()
            
            response = requests.get(
                self.api_url,
                headers=self.api_headers,
                timeout=30  # 30초 타임아웃
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"부스 데이터 API 호출 성공: {len(data.get('data', {}).get('boothDetails', []))}개 부스")
                return data
            else:
                logger.error(f"API 호출 실패: HTTP {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API 호출 중 네트워크 오류: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"API 응답 JSON 파싱 오류: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"부스 데이터 가져오기 중 예상치 못한 오류: {str(e)}")
            return None
    
    def save_booth_data(self, api_data: Dict) -> bool:
        """
        API 데이터를 DB에 저장합니다.
        
        Args:
            api_data (Dict): API에서 받은 데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            booth_details = api_data.get('data', {}).get('boothDetails', [])
            
            if not booth_details:
                logger.warning("저장할 부스 데이터가 없습니다.")
                return True
            
            with transaction.atomic():
                saved_count = 0
                updated_count = 0
                
                for booth_data in booth_details:
                    success = self._save_single_booth(booth_data)
                    if success:
                        # 부스가 새로 생성되었는지 업데이트되었는지 확인하는 로직은
                        # _save_single_booth 메서드에서 처리
                        saved_count += 1
                
                logger.info(f"부스 데이터 저장 완료: {saved_count}개 부스 처리됨")
                return True
                
        except Exception as e:
            logger.error(f"부스 데이터 저장 중 오류: {str(e)}")
            return False
    
    def _save_single_booth(self, booth_data: Dict) -> bool:
        try:
            booth_name = booth_data.get('boothName')
            all_table = booth_data.get('boothAllTable', 0)
            usage_table = booth_data.get('boothUsageTable', 0)
            menus = booth_data.get('Menus', [])
            
            if not booth_name:
                logger.warning("부스 이름이 없는 데이터를 건너뜁니다.")
                return False
            
            # 부스 찾기 또는 생성 (이름으로 매칭)
            booth, booth_created = Booth.objects.get_or_create(
                name=booth_name,
                defaults={
                    'category': Booth.Category.BOOTH,
                    'is_dorder': True,  # dorder 시스템에서 관리되는 부스로 표시
                }
            )
            
            # 부스 상세 정보 업데이트 또는 생성
            booth_detail, detail_created = BoothDetail.objects.update_or_create(
                booth=booth,
                defaults={
                    'all_table': all_table,
                    'usage_table': usage_table,
                    'can_usage': usage_table < all_table,  # 사용 가능한 테이블이 있으면 True
                    'description': f'dorder 시스템에서 자동 동기화된 부스 정보 (마지막 업데이트: {timezone.now()})'
                }
            )
            
            # 메뉴 정보 업데이트
            self._update_booth_menus(booth, menus)
            
            action = "생성" if booth_created else "업데이트"
            logger.debug(f"부스 {action}: {booth_name} (테이블: {usage_table}/{all_table})")
            
            return True
            
        except Exception as e:
            logger.error(f"단일 부스 데이터 저장 중 오류: {str(e)}")
            return False
    
    def _update_booth_menus(self, booth: Booth, menus_data: List[Dict]) -> None:
        try:
            for menu_data in menus_data:
                menu_name = menu_data.get('menuName')
                ingredient_reminder = menu_data.get('menuIngredidentReminder', 0)
                sales_quantity = menu_data.get('menuSalesQuantity', 0)
                
                if not menu_name:
                    continue
                
                # 메뉴 업데이트 또는 생성
                menu, menu_created = Menu.objects.update_or_create(
                    booth=booth,
                    name=menu_name,
                    defaults={
                        'ingredient': ingredient_reminder,
                        'sold': sales_quantity,
                        'price': 0,  # API에서 가격 정보가 없으므로 기본값 0
                    }
                )
                
                action = "생성" if menu_created else "업데이트"
                logger.debug(f"메뉴 {action}: {booth.name} - {menu_name} (재고: {ingredient_reminder}, 판매량: {sales_quantity})")
                
        except Exception as e:
            logger.error(f"메뉴 업데이트 중 오류: {str(e)}")
    
    def sync_once(self) -> bool:
        logger.info("부스 데이터 동기화 시작")
        start_time = time.time()
        
        # API에서 데이터 가져오기
        api_data = self.fetch_booth_data()
        if not api_data:
            logger.error("API 데이터를 가져올 수 없어 동기화를 중단합니다.")
            return False
        
        # 데이터 저장
        success = self.save_booth_data(api_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if success:
            logger.info(f"부스 데이터 동기화 완료 (소요시간: {duration:.2f}초)")
        else:
            logger.error(f"부스 데이터 동기화 실패 (소요시간: {duration:.2f}초)")
        
        return success
    
    def _sync_loop(self) -> None:
        logger.info(f"부스 데이터 동기화 시작: {self.sync_interval}초 간격으로 실행")
        
        while self.is_running:
            try:
                self.sync_once()
            except Exception as e:
                logger.error(f"동기화 루프 중 예상치 못한 오류: {str(e)}")
            
            # 다음 동기화까지 대기
            for _ in range(self.sync_interval):
                if not self.is_running:
                    break
                time.sleep(1)
        
        logger.info("부스 데이터 동기화 중지됨")
    
    def start_sync(self) -> bool:
        if self.is_running:
            logger.warning("동기화가 이미 실행 중입니다.")
            return False
        
        try:
            self.is_running = True
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.sync_thread.start()
            logger.info("부스 데이터 동기화 시작됨")
            return True
        except Exception as e:
            logger.error(f"동기화 시작 중 오류: {str(e)}")
            self.is_running = False
            return False
    
    def stop_sync(self) -> bool:
        if not self.is_running:
            logger.warning("동기화가 실행 중이 아닙니다.")
            return False
        
        try:
            self.is_running = False
            if self.sync_thread and self.sync_thread.is_alive():
                self.sync_thread.join(timeout=10)  # 최대 10초 대기
            
            logger.info("부스 데이터 동기화 중지됨")
            return True
        except Exception as e:
            logger.error(f"동기화 중지 중 오류: {str(e)}")
            return False
    
    def get_status(self) -> Dict:
        return {
            'is_running': self.is_running,
            'sync_interval': self.sync_interval,
            'api_url': self.api_url,
            'thread_alive': self.sync_thread.is_alive() if self.sync_thread else False,
            'last_update': timezone.now().isoformat()
        }


# 전역 동기화 인스턴스
_synchronizer = None


def get_synchronizer() -> BoothDataSynchronizer:
    global _synchronizer
    if _synchronizer is None:
        _synchronizer = BoothDataSynchronizer()
    return _synchronizer


def start_booth_sync() -> bool:
    synchronizer = get_synchronizer()
    return synchronizer.start_sync()


def stop_booth_sync() -> bool:
    synchronizer = get_synchronizer()
    return synchronizer.stop_sync()


def sync_booth_data_once() -> bool:
    synchronizer = get_synchronizer()
    return synchronizer.sync_once()


def get_sync_status() -> Dict:
    synchronizer = get_synchronizer()
    return synchronizer.get_status()


# Django 앱 시작 시 자동으로 동기화 시작
def auto_start_sync():
    try:
        success = start_booth_sync()
        if success:
            logger.info("앱 시작 시 부스 데이터 동기화 자동 시작됨")
        else:
            logger.warning("앱 시작 시 부스 데이터 동기화 자동 시작 실패")
    except Exception as e:
        logger.error(f"자동 동기화 시작 중 오류: {str(e)}")
