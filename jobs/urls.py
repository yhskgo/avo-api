from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('jobs', views.create_job, name='create_job'),
    path('jobs/<uuid:event_id>', views.get_job_status, name='get_job_status'),
]