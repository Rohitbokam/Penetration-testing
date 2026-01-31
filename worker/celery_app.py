import os
from celery import Celery

# Configure Celery to use Redis as broker and backend
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "threatlens_worker",
    broker=redis_url,
    backend=redis_url,
    include=["worker.tasks.scanning"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
