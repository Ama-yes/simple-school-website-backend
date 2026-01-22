from celery import Celery
from app.core.config import settings


celery_worker = Celery("school_worker", broker=settings.redis_worker_url, backend=settings.redis_worker_url)

celery_worker.conf.task_routes = {"aoo.worker.tasks.*": {"queue": "main-queue"}}