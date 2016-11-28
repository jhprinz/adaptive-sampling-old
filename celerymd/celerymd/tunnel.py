import logging
import re
from sshtunnel import SSHTunnelForwarder
import subprocess
import os

logger = logging.getLogger(__name__)

tunnel_server = None

tunnel_process = None


def create_server(
        redis_server,
        local_node_port,
        ssh_password=None,
        ssh_host_key=None,
):
    global tunnel_server
    logger.info('create tunnel object')

    reg_ex = re.compile('([a-zA-Z0-9_]+)@([a-zA-Z0-9\.\-\_]+):([0-9]+)')

    redis_server_user, redis_server, redis_port = \
        reg_ex.findall(redis_server)[0]

    tunnel_server = SSHTunnelForwarder(
        redis_server,
        ssh_username=redis_server_user,
        ssh_password=ssh_password,
        local_bind_address=('127.0.0.1', local_node_port),
        remote_bind_address=('127.0.0.1', int(redis_port))
    )


def open_tunnel(**kwargs):
    global tunnel_server
    logger.info('Create tunnel')
    tunnel_server.start()
    logger.info('tunnel established at port %s' % str(tunnel_server.local_bind_address))


def close_tunnel(**kwargs):
    global tunnel_server
    logger.info('Shut down tunnel')
    tunnel_server.stop()
    logger.info('Tunnel removed')


def bash_tunnel_open(
        redis_server,
        local_node_port):

    global tunnel_process

    reg_ex = re.compile('([a-zA-Z0-9_]+)@([a-zA-Z0-9\.\-\_]+):([0-9]+)')

    redis_server_user, redis_server, redis_port = \
        reg_ex.findall(redis_server)[0]

    # FNULL = open(os.devnull, 'w')

    bashCommand = " ssh -N -L%d:localhost:%d %s@%s" % (
        local_node_port, int(redis_port), redis_server_user, redis_server
    )

    tunnel_process = subprocess.Popen(
        bashCommand.split()
    )


def bash_tunnel_close():
    global tunnel_process

    tunnel_process.kill()


class BashTunnel(object):
    host_reg_ex = re.compile('([a-zA-Z0-9_]+)@([a-zA-Z0-9\.\-\_]+):([0-9]+)')

    def __init__(self, redis_server, local_node_port):
        self._redis_server = redis_server
        self._local_node_port = local_node_port
        self.process = None

    @property
    def local_node_port(self):
        return self._local_node_port

    @property
    def redis_server(self):
        return self._redis_server

    @property
    def cmd(self):

        redis_server_user, redis_server, redis_port = \
            BashTunnel.host_reg_ex.findall(self.redis_server)[0]

        return " ssh -N -L%d:localhost:%d %s@%s" % (
            self.local_node_port, int(redis_port),
            redis_server_user, redis_server
        )

    def open(self, **kwargs):
        self.process = subprocess.Popen(
            self.cmd.split()
        )

    def close(self, **kwargs):
        if self.process:
            self.process.kill()
