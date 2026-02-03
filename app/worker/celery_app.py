"""
Celery application for async task processing.
Producer-Consumer pattern: FastAPI pushes, Celery processes.
"""
from celery import Celery
from app.core.config import settings

# Initialize Celery app only if REDIS_URL is configured
celery_app = None

if settings.REDIS_URL:
    celery_app = Celery(
        "philia_thrifts",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
    )

    # Celery configuration
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,  # 5 minutes max per task
        task_soft_time_limit=270,  # Soft limit at 4.5 minutes
        worker_prefetch_multiplier=1,  # Fair task distribution
        worker_max_tasks_per_child=1000,  # Prevent memory leaks
        task_acks_late=True,  # Acknowledge after task completion
        task_reject_on_worker_lost=True,  # Retry if worker crashes
    )

    # Auto-discover tasks from app.worker.tasks module
    celery_app.autodiscover_tasks(["app.worker"])
else:
    # Create a dummy Celery app for when Redis is not configured
    # This allows the app to import without errors
    celery_app = Celery("philia_thrifts")
    celery_app.conf.broker_url = "memory://"
    celery_app.conf.result_backend = "cache"
