from celery import Celery
from celery.signals import worker_process_init
import logging

logger = logging.getLogger(__name__)


app = Celery('tasks', backend='redis://localhost:6379/0', broker='amqp://')
app.config_from_object('celeryconfig')


# This will force each child process to have a sep

def _redo_uuid(**kwargs):
    import openpathsampling.netcdfplus as npl
    # logger.info('OLD UUID `%s`' % npl.StorableObject.INSTANCE_UUID)
    npl.StorableObject.initialize_uuid()
    logger.info('NEW UUID `%s`' % npl.StorableObject.INSTANCE_UUID)

# need to use registered instance for sender argument.
worker_process_init.connect(_redo_uuid)


@app.task
def generate(engine, template, ensemble):
    engine.initialize('CPU')
    traj = engine.generate(template, ensemble.can_append)
    return traj

