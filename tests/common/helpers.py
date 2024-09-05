import os
import pydbus
import logging
import docker
from mass import PortController, NGINX, HTTPD, PORT, PROXY

# Logger configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get a specific logger for the package
logger = logging.getLogger('MASS testing')


BUS = pydbus.SystemBus()
FIREBUS = BUS.get('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1')
ZONE = FIREBUS.getDefaultZone()

DOCKER = docker.from_env()
VOLUME = {
            os.getcwd()+'../html': {'bind': '/var/www/localhost/htdocs', 'mode': 'ro'}
        }

PORT_NGINX = {PORT[PROXY]:PORT[NGINX]}
PORT_HTTPD = {PORT[PROXY]:PORT[HTTPD]}

def get_container(container):
    try:
        return DOCKER.containers.get(container)
    except Exception:
        return False

# list sin argumento devuelve por defecto solo los 'running'
def get_containers():
    return DOCKER.containers.list()

def get_masquerade():
    return FIREBUS.queryMasquerade(ZONE)

def get_ports():
    return FIREBUS.getForwardPorts(ZONE)

def set_masquerade(state):
    print(state)
    print(get_masquerade())
    if (not get_masquerade() and state): 
        FIREBUS.addMasquerade(ZONE, 0)
    elif (get_masquerade() and not state):
        FIREBUS.removeMasquerade(ZONE)

def set_ports(nginx_udp, nginx_tcp, httpd_udp, httpd_tcp):
    ports = {
        "NGINX": {
            "udp": nginx_udp,
            "tcp": nginx_tcp
        },
        "HTTPD": {
            "udp": httpd_udp,
            "tcp": httpd_tcp
        }
    }

    for container, protocols in ports.items():
        for protocol in protocols:
            print(f"container {container}, protocols: {protocol}")
            if protocol:
                try:
                    FIREBUS.addForwardPort('', PORT[PROXY], protocol, PORT[container], '', 0)
                except Exception as e:
                    if 'GDBus.Error:org.fedoraproject.FirewallD1.Exception: ALREADY_ENABLED' in str(e):
                        pass
                else:
                    logger.error(f"The port could not be added: {str(e)}")
            else:
                try:
                    FIREBUS.removeForwardPort('', PORT[PROXY], protocol, PORT[container], '', 0)
                except Exception as e:
                    if 'GDBus.Error:org.fedoraproject.FirewallD1.Exception: ALREADY_ENABLED' in str(e):
                        pass
                else:
                    logger.error(f"The port could not be removed: {str(e)}")
