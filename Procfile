web: daphne -b 0.0.0.0 -p $PORT restaurant_system.asgi:application
worker: celery worker --app=restaurant_system.celery --loglevel=info
beat: celery beat --app=restaurant_system.celery --loglevel=info