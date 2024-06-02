import os
import time
import logging
import docker
from .port_controller import PortController
from .decorators import apply_timing_to_methods, timing_decorator
from .config import PORT, NGINX, HTTPD, PROXY, logger

@apply_timing_to_methods(timing_decorator)
class ContainerController:

    def __init__(self, container=NGINX):
        self.client = docker.from_env()
        self.volume = {
            os.getcwd()+'/html': {'bind': '/var/www/localhost/htdocs', 'mode': 'ro'}
        }
        self.port_bindings_httpd = {PORT[PROXY]:PORT[HTTPD]}
        self.port_bindings_nginx = {PORT[PROXY]:PORT[NGINX]}

        self.create_container(container.lower())
        self.port_controller = PortController(container.upper())

    def close(self):
        try:
            self.remove_container(self.active_container)
        except Exception as e:
            logger.error(f"close: {str(e)}")


    def create_container(self, container_name):
        """Crea y ejecuta un contenedor a partir de una imagen."""

        try:
            container = self.client.containers.get(container_name)
            if container:
                self.remove_container(container)

        except docker.errors.NotFound as e:
            pass
        except Exception as e:
            logger.error(f"Error getting the {container_name} container: {str(e)}")
            raise Exception

        ports = self.port_bindings_nginx if container_name == NGINX.lower() else self.port_bindings_httpd
        try:
            container = self.client.containers.run(container_name, name=container_name, detach=True, auto_remove=True, volumes=self.volume, ports=ports)
            logger.info(f"{container.name} container settled up.")
            self.active_container = container
        except docker.errors.ImageNotFound:
            logger.error(f"The {container_name} image was not found.")            
        except Exception as e:
            logger.error(f"Error creating the {container_name} container: {str(e)}")
            
    def remove_container(self, container):
        try:
            container.remove(force=True)
            logger.info(f"The {container.name} was removed.")

        except docker.errors.APIError as e:
            if 'removal of container' in str(e) and 'is already in progress' in str(e):
                pass
            logger.error(f"Docker API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
