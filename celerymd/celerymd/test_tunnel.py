import logging

from celery import Celery
from celery.signals import worker_process_init, celeryd_init, worker_shutdown

import tunnel

import time
import os

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------------

# TODO: Should be move to config file at some point

redis_server = 'jprinz@sheep.imp.fu-berlin.de:6379'
local_node_port = 6383  # the port where the worker connects locally

# read from file. This is kind of bad, but ssh_tunnel does not support
# known_hosts. Need to find a way around that.

keyfile = os.path.join(os.environ['HOME'], '.ssh', 'known_hosts')
ssh_password = open('pw.pw').read()

known_hosts_file = open(keyfile).readlines()

ssh_host_key = None

for line in known_hosts_file:
    if 'sheep.imp' in line:
        ssh_host_key = line.strip()

# ------------------------------------------------------------------------------
# CREATE CELERY APP
# ------------------------------------------------------------------------------

# Create a function to initialize a SHH tunnel
# this works but I think this way is legacy and has problems shutting down
# gracefully. Will be reimplemented using a custom `bootstep`

tunnel.create_server(
    redis_server,
    local_node_port,
    ssh_password=ssh_password,
    # ssh_host_key=ssh_host_key
)


tunnel.open_tunnel()

print tunnel.tunnel_server

time.sleep(3)

tunnel.close_tunnel()
