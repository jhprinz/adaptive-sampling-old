from celery import Celery
import logging

logger = logging.getLogger(__name__)


app = Celery('tasks', backend='redis://localhost:6379/0', broker='amqp://')
app.config_from_object('celeryconfig')

