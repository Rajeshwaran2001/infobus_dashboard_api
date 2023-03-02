from celery import Celery

app = Celery('infobus_dashboard_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
