import os
import time
import logging
import docker
from .decorators import apply_timing_to_methods, timing_decorator
from .config import PORT, NGINX, HTTPD, PROXY, logger

@apply_timing_to_methods(timing_decorator)
class ContainerController:

    def __init__(self, container=NGINX):
        self._client = docker.from_env()
        self._volume = {
            os.getcwd()+'/html': {'bind': '/var/www/localhost/htdocs', 'mode': 'ro'}
        }
        self._port_bindings_httpd = {PORT[PROXY]:PORT[HTTPD]}
        self._port_bindings_nginx = {PORT[PROXY]:PORT[NGINX]}

        running_containers = self._client.containers.list()
        for running_container in running_containers:
            if running_container.name is NGINX.lower() or running_container.name is HTTPD.lower():
                self.remove_container(running_container)
                logger.info(f"borrado al iniciar la clase: {running_container.name}")

        self._active_containers = []
        self.create_container(container.lower())

    def close(self):
        for container in self._active_containers[:]:
            self.remove_container(container)
            logger.info(f"Erasing: {container.name}")

    def create_container(self, container_name):
        """Crea y ejecuta un contenedor a partir de una imagen."""

        try:
            container = self._client.containers.get(container_name)
            if container:
                self.remove_container(container)

        except docker.errors.NotFound as e:
            pass
        except Exception as e:
            logger.error(f"Error getting the {container_name} container: {str(e)}")
            raise Exception

        ports = self._port_bindings_nginx if container_name == NGINX.lower() else self._port_bindings_httpd
        try:
            container = self._client.containers.run(container_name, name=container_name, detach=True, auto_remove=True, volumes=self._volume, ports=ports)
            logger.info(f"{container.name} container settled up.")
            self._active_containers.append(container)
        except docker.errors.ImageNotFound:
            logger.error(f"The {container_name} image was not found.")            
        except Exception as e:
            logger.error(f"Error creating the {container_name} container: {str(e)}")
            
    def remove_container(self, container):
        try:
            container.remove(force=True)
            if container in self._active_containers:
                self._active_containers.remove(container)
            logger.info(f"The {container.name} was removed.")

        except docker.errors.APIError as e:
            if 'removal of container' in str(e) and 'is already in progress' in str(e):
                logger.info(f"The {container.name} removing is already in progress.")
                pass
            logger.error(f"Docker API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")

    def get_current_container(self):
        return self._active_containers[0]