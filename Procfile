web: python -u main.py
worker: celery -A app.worker.celery_app worker --loglevel=info --concurrency=2
