import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('project')

#settings.py에서 CELERY로 시작하는 설정값을 가져옴
app.config_from_object('django.conf:settings', namespace='CELERY') 

# 모든 celery shared_task 데코레이터가 적용된 테스크 수집
app.autodiscover_tasks() 