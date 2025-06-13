import uuid
from django.db import models
from django.utils import timezone


class Job(models.Model):
    STATUS_CHOICES = [
        ('pending', '대기 중'),
        ('processing', '처리 중'),
        ('completed', '완료'),
        ('failed', '실패'),
    ]
    
    event_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='이벤트 ID'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='상태'
    )
    
    message = models.TextField(
        null=True,
        blank=True,
        verbose_name='상태 메시지'
    )
    
    result = models.JSONField(
        null=True,
        blank=True,
        verbose_name='처리 결과'
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='생성일시'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        db_table = 'jobs'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.event_id} - {self.get_status_display()}"
    
    @property
    def is_completed(self):
        return self.status in ['completed', 'failed']