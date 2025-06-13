import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from jobs.models import Job


class JobModelTest(TestCase):
    """Test Job model"""
    
    def test_job_creation(self):
        """Test job creation with valid data"""
        job = Job.objects.create(
            event_id=uuid.uuid4(),
            status='pending'
        )
        self.assertEqual(job.status, 'pending')
        self.assertIsNotNone(job.event_id)
        self.assertIsNotNone(job.created_at)
        self.assertIsNotNone(job.updated_at)
    
    def test_job_str_representation(self):
        """Test job string representation"""
        event_id = uuid.uuid4()
        job = Job.objects.create(event_id=event_id, status='pending')
        self.assertTrue("Job" in str(job))
        self.assertTrue("pending" in str(job))


class JobAPITest(APITestCase):
    """Test Job API endpoints"""
    
    @patch('jobs.tasks.process_guideline_job.delay')
    def test_create_job_success(self, mock_task):
        """Test successful job creation"""
        response = self.client.post('/api/jobs', {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('event_id', response.data)
        
        # Verify job was created in database
        event_id = response.data['event_id']
        job = Job.objects.get(event_id=event_id)
        self.assertEqual(job.status, 'pending')
        
        # Verify task was queued
        mock_task.assert_called_once_with(event_id)
    
    def test_get_job_success(self):
        """Test successful job retrieval"""
        # Create a job
        job = Job.objects.create(
            event_id=uuid.uuid4(),
            status='completed',
            message='작업이 완료되었습니다.',
            result={
                'summary': {'content': 'Test summary'},
                'checklist': {'categories': []}
            }
        )
        
        response = self.client.get(f'/api/jobs/{job.event_id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['event_id'], str(job.event_id))
        self.assertEqual(response.data['status'], 'completed')
        self.assertIn('result', response.data)
    
    def test_get_job_not_found(self):
        """Test job not found scenario"""
        non_existent_id = uuid.uuid4()
        response = self.client.get(f'/api/jobs/{non_existent_id}')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
