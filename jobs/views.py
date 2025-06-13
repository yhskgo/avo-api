from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.openapi import AutoSchema

from .models import Job
from .tasks import process_guideline_job


@extend_schema(
    operation_id='create_job',
    summary='Create a new guideline processing job',
    description='Creates a new job for processing guidelines and returns an event_id in under 200ms',
    responses={
        201: OpenApiResponse(
            response={'type': 'object', 'properties': {'event_id': {'type': 'string', 'format': 'uuid'}}},
            description='Job created successfully'
        )
    },
    tags=['Jobs']
)
@api_view(['POST'])
def create_job(request):
    """
    새로운 guideline-ingest job을 생성하고 Celery 큐에 등록
    < 200ms 응답 보장
    """
    # Job 생성
    job = Job.objects.create(status='pending')
    
    # Celery task 비동기 실행 (FIFO 큐)
    process_guideline_job.delay(str(job.event_id))
    
    return Response(
        {'event_id': str(job.event_id)},
        status=status.HTTP_201_CREATED
    )


@extend_schema(
    operation_id='get_job_status',
    summary='Get job status and results',
    description='Retrieve the current status and results of a job by event_id',
    responses={
        200: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'event_id': {'type': 'string', 'format': 'uuid'},
                    'status': {'type': 'string', 'enum': ['pending', 'processing', 'completed', 'failed']},
                    'message': {'type': 'string'},
                    'result': {'type': 'object'},
                    'created_at': {'type': 'string', 'format': 'date-time'},
                    'updated_at': {'type': 'string', 'format': 'date-time'},
                }
            },
            description='Job status retrieved successfully'
        ),
        404: OpenApiResponse(description='Job not found')
    },
    tags=['Jobs']
)
@api_view(['GET'])
def get_job_status(request, event_id):
    """
    Job 상태 및 결과 조회
    """
    job = get_object_or_404(Job, event_id=event_id)
    
    response_data = {
        'event_id': str(job.event_id),
        'status': job.status,
        'created_at': job.created_at.isoformat(),
        'updated_at': job.updated_at.isoformat(),
    }
    
    # 상태별 응답 처리
    if job.status == 'pending':
        response_data['message'] = '작업이 대기 중입니다.'
        
    elif job.status == 'processing':
        response_data['message'] = '작업을 처리하고 있습니다.'
        # 진행 상황이 있다면 포함
        if job.result and 'steps_completed' in job.result:
            response_data['progress'] = {
                'steps_completed': job.result['steps_completed'],
                'current_step': get_current_step(job.result['steps_completed'])
            }
            
    elif job.status == 'completed':
        response_data['message'] = '작업이 완료되었습니다.'
        if job.result:
            response_data['result'] = job.result
            
    elif job.status == 'failed':
        response_data['message'] = '작업 처리 중 오류가 발생했습니다.'
        if job.result and 'error' in job.result:
            response_data['error'] = job.result['error']
            response_data['failed_at'] = job.result.get('failed_at')
    
    return Response(response_data)


def get_current_step(steps_completed):
    """
    완료된 단계를 바탕으로 현재 진행 중인 단계 반환
    """
    if not steps_completed:
        return 'summary_generation'
    
    if 'summary_generated' not in steps_completed:
        return 'summary_generation'
    elif 'checklist_generated' not in steps_completed:
        return 'checklist_generation'
    else:
        return 'finalizing'