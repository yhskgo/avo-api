# Generated by Django 4.2.7 on 2025-06-12 04:52

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='이벤트 ID')),
                ('status', models.CharField(choices=[('pending', '대기 중'), ('processing', '처리 중'), ('completed', '완료'), ('failed', '실패')], default='pending', max_length=20, verbose_name='상태')),
                ('result', models.JSONField(blank=True, null=True, verbose_name='처리 결과')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='생성일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
            ],
            options={
                'verbose_name': 'Job',
                'verbose_name_plural': 'Jobs',
                'db_table': 'jobs',
                'ordering': ['-created_at'],
            },
        ),
    ]
