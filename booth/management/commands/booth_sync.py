"""
부스 데이터 동기화 관리를 위한 Django Management Command
"""

from django.core.management.base import BaseCommand, CommandError
from booth.dorders import (
    start_booth_sync, 
    stop_booth_sync, 
    sync_booth_data_once, 
    get_sync_status
)
import json


class Command(BaseCommand):
    help = '부스 데이터 동기화를 관리합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['start', 'stop', 'sync', 'status'],
            help='수행할 작업을 선택하세요 (start: 동기화 시작, stop: 동기화 중지, sync: 한 번 동기화, status: 상태 확인)'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        try:
            if action == 'start':
                self.stdout.write('부스 데이터 동기화를 시작합니다...')
                success = start_booth_sync()
                if success:
                    self.stdout.write(
                        self.style.SUCCESS('부스 데이터 동기화가 성공적으로 시작되었습니다.')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('부스 데이터 동기화 시작에 실패했습니다.')
                    )
            
            elif action == 'stop':
                self.stdout.write('부스 데이터 동기화를 중지합니다...')
                success = stop_booth_sync()
                if success:
                    self.stdout.write(
                        self.style.SUCCESS('부스 데이터 동기화가 성공적으로 중지되었습니다.')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('부스 데이터 동기화 중지에 실패했습니다.')
                    )
            
            elif action == 'sync':
                self.stdout.write('부스 데이터를 한 번 동기화합니다...')
                success = sync_booth_data_once()
                if success:
                    self.stdout.write(
                        self.style.SUCCESS('부스 데이터 동기화가 성공적으로 완료되었습니다.')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('부스 데이터 동기화에 실패했습니다.')
                    )
            
            elif action == 'status':
                self.stdout.write('부스 데이터 동기화 상태를 확인합니다...')
                status = get_sync_status()
                self.stdout.write(
                    self.style.SUCCESS(f'동기화 상태:\n{json.dumps(status, indent=2, ensure_ascii=False)}')
                )
        
        except Exception as e:
            raise CommandError(f'명령 실행 중 오류가 발생했습니다: {str(e)}')