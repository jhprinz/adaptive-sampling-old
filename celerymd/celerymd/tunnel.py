import logging
import re
from sshtunnel import SSHTunnelForwarder


logger = logging.getLogger(__name__)

tunnel_server = None


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
