import os
from celery import Celery
from django.conf import settings

# Django 설정 모듈 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avo_api.settings')

# Celery 앱 생성
app = Celery('avo_api')

# Django 설정을 사용하여 Celery 구성
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery 설정
app.conf.update(
    # Redis를 broker와 result backend로 사용
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    
    # 작업 결과 만료 시간 (1시간)
    result_expires=3600,
    
    # 작업 직렬화 형식
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # 시간대 설정
    timezone='Asia/Seoul',
    enable_utc=True,
    
    # FIFO 큐 설정 (우선순위 없음)
    task_routes={
        'jobs.tasks.guideline_ingest_task': {'queue': 'guideline_queue'},
    },
    
    # Worker 설정
    worker_prefetch_multiplier=1,  # 한 번에 하나씩 처리 (FIFO 보장)
    task_acks_late=True,           # 작업 완료 후 ACK
    worker_disable_rate_limits=False,
    
    # 재시도 설정
    task_reject_on_worker_lost=True,
    
    # 로깅 설정
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

# Django 앱에서 태스크 자동 발견
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """디버그용 태스크"""
    print(f'Request: {self.request!r}')
    return 'Debug task completed'


# Celery 시작 시 호출되는 신호
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    주기적 작업 설정 (필요한 경우)
    """
    # 예: 매 10분마다 실행
    # sender.add_periodic_task(600.0, debug_task.s(), name='debug every 10 minutes')
    pass