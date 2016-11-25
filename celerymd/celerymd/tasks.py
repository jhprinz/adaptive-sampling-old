import logging

from celery import Celery
from celery.signals import worker_process_init, celeryd_init, worker_shutdown

from util import _redo_uuid
import tunnel

import os

import simtk.openmm
import simtk.openmm.app
import mdtraj as md


logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------------

# TODO: Should be move to config file at some point

redis_server = 'jprinz@shark.imp.fu-berlin.de:6379'
local_node_port = 6383  # the port where the worker connects locally


# read from file. This is kind of bad, but ssh_tunnel does not support
# known_hosts. Need to find a way around that.
keyfile = '/Users/jan-hendrikprinz/.ssh/known_hosts'
ssh_password = open('pw').read()


# ------------------------------------------------------------------------------
# CREATE CELERY APP
# ------------------------------------------------------------------------------

server_str = 'redis://localhost:%d/0' % local_node_port

app = Celery('tasks', backend=server_str, broker=server_str)
app.config_from_object('celeryconfig')

# need to use registered instance for sender argument.
worker_process_init.connect(_redo_uuid)

# Create a function to initialize a SHH tunnel
# this works but I think this way is legacy and has problems shutting down
# gracefully. Will be reimplemented using a custom `bootstep`

tunnel.create_server(
    redis_server,
    ssh_password,
    local_node_port)

celeryd_init.connect(tunnel.open_tunnel)
worker_shutdown.connect(tunnel.close_tunnel)


# ------------------------------------------------------------------------------
# DEFINE TASKS
# ------------------------------------------------------------------------------

@app.task
def directory(mypath):
    return os.listdir(mypath)


@app.task
def generate(
        dcd_filename,
        steps,
        system_xml,
        integrator_xml,
        initial_pdb,
        platform,
        properties):
    # fix to send pdb file as string and not filename
    pdb = md.load(initial_pdb)

    simulation = simtk.openmm.app.Simulation(
        topology=pdb.topology.to_openmm(),
        system=simtk.openmm.XmlSerializer.deserialize(system_xml),
        integrator=simtk.openmm.XmlSerializer.deserialize(integrator_xml),
        platform=simtk.openmm.Platform.getPlatformByName(platform),
        platformProperties=properties
    )
    simulation.reporters.append(simtk.openmm.app.DCDReporter(dcd_filename, 1000))
    simulation.step(steps)

    return {'Results': 'something'}


@app.task(name='openpathsampling.engine.celery.tasks.generate')
def generate(engine, template, ensemble, init_args=None, init_kwargs=None):
    if init_args is None:
        init_args = []
    if init_kwargs is None:
        init_kwargs = {}

    engine.initialize(*init_args, **init_kwargs)
    traj = engine.generate(template, ensemble.can_append)
    return traj
