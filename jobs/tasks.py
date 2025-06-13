from celery import shared_task
from django.utils import timezone
import logging

from .models import Job
from .services.gpt_service import GPTService

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='jobs.tasks.process_guideline_job')
def process_guideline_job(self, event_id):
    """
    Guideline ingest 작업을 처리하는 Celery task
    FIFO 큐에서 처리되며 2단계 GPT 체인을 실행합니다.
    """
    try:
        # Job 조회 및 상태를 processing으로 변경
        job = Job.objects.get(event_id=event_id)
        job.status = 'processing'
        job.save()
        
        logger.info(f"🚀 Starting job processing for event_id: {event_id}")
        
        # GPT 서비스 초기화
        gpt_service = GPTService()
        
        # 1단계: 가이드라인 요약 생성
        logger.info(f"📝 Step 1: Generating summary for event_id: {event_id}")
        summary = gpt_service.generate_summary()
        
        # 중간 상태 저장 (요약 완료)
        job.result = {
            'summary': summary,
            'steps_completed': ['summary_generated']
        }
        job.save()
        logger.info(f"✅ Summary generated for event_id: {event_id}")
        
        # 2단계: 요약을 바탕으로 체크리스트 생성
        logger.info(f"📋 Step 2: Generating checklist for event_id: {event_id}")
        checklist = gpt_service.generate_checklist(summary)
        
        # 최종 결과 저장
        result = {
            'summary': summary,
            'checklist': checklist,
            'processed_at': timezone.now().isoformat(),
            'steps_completed': ['summary_generated', 'checklist_generated']
        }
        
        job.result = result
        job.status = 'completed'
        job.save()
        
        logger.info(f"🎉 Successfully completed job processing for event_id: {event_id}")
        return result
        
    except Job.DoesNotExist:
        error_msg = f"❌ Job not found for event_id: {event_id}"
        logger.error(error_msg)
        raise Exception(error_msg)
        
    except Exception as exc:
        error_msg = f"❌ Error processing job {event_id}: {str(exc)}"
        logger.error(error_msg)
        
        # Job 상태를 failed로 변경
        try:
            job = Job.objects.get(event_id=event_id)
            job.status = 'failed'
            job.result = {
                'error': str(exc),
                'failed_at': timezone.now().isoformat()
            }
            job.save()
            logger.info(f"💾 Updated job status to failed for event_id: {event_id}")
        except Job.DoesNotExist:
            logger.error(f"Could not update job status to failed for event_id: {event_id}")
            
        raise exc


# Celery.py에서 사용되는 별칭 함수
@shared_task(bind=True, name='jobs.tasks.guideline_ingest_task')
def guideline_ingest_task(self, event_id):
    """
    Celery routing을 위한 별칭 함수
    실제 작업은 process_guideline_job에서 수행
    """
    return process_guideline_job(event_id)