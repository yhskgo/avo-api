import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from jobs.models import Job
from jobs.tasks import process_guideline_job
from jobs.services.gpt_service import GPTService


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
        self.assertEqual(str(job), f"Job {event_id} - pending")


class JobAPITest(APITestCase):
    """Test Job API endpoints"""
    
    def test_create_job_success(self):
        """Test successful job creation"""
        url = reverse('jobs:create_job')
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('event_id', response.data)
        
        # Verify job was created in database
        event_id = response.data['event_id']
        job = Job.objects.get(event_id=event_id)
        self.assertEqual(job.status, 'pending')
    
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
        
        url = reverse('jobs:get_job_status', kwargs={'event_id': job.event_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['event_id'], str(job.event_id))
        self.assertEqual(response.data['status'], 'completed')
        self.assertIn('result', response.data)
    
    def test_get_job_not_found(self):
        """Test job not found scenario"""
        non_existent_id = uuid.uuid4()
        url = reverse('jobs:get_job_status', kwargs={'event_id': non_existent_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GPTServiceTest(TestCase):
    """Test GPT Service"""
    
    @patch('jobs.services.gpt_service.openai')
    def test_generate_summary_success(self, mock_openai):
        """Test successful summary generation"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "title": "Test Guidelines",
            "content": "Test summary content",
            "key_points": ["Point 1", "Point 2"],
            "word_count": 50
        }
        '''
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        service = GPTService()
        service.use_fallback = False
        service.model_name = "gpt-4o-mini"
        result = service.generate_summary("Test guideline content")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test Guidelines')
        self.assertEqual(result['content'], 'Test summary content')
        self.assertEqual(len(result['key_points']), 2)


class IntegrationTest(APITestCase):
    """Integration tests"""
    
    @patch('jobs.tasks.process_guideline_job.delay')
    def test_full_job_workflow(self, mock_task):
        """Test complete job workflow from creation to completion"""
        # Create job
        create_url = reverse('jobs:create_job')
        create_response = self.client.post(create_url, {}, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        event_id = create_response.data['event_id']
        
        # Verify task was queued
        mock_task.assert_called_once_with(event_id)
        
        # Check initial status
        status_url = reverse('jobs:get_job_status', kwargs={'event_id': event_id})
        status_response = self.client.get(status_url)
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_response.data['status'], 'pending')
