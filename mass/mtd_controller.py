import time
import random
from .config import NGINX, HTTPD, logger, get_shutdown
from .container_controller import ContainerController
from .port_controller import PortController

class MTDController:
    def __init__(self, duration, lower, upper):
        if lower > upper:
            logger.error("The lower bound cannot be higher than the upper bound.")
            raise ValueError("The lower bound cannot be higher than the upper bound.")
            
        self.container_controller = ContainerController()
        self.port_controller = PortController()
        self.duration = duration
        self.lower = lower
        self.upper = upper

    def __del__(self):
        self.container_controller.close()
        self.port_controller.close()

    def switch(self):
        old_container = self.container_controller.active_container
        if self.container_controller.active_container.name == NGINX.lower():
            logger.info("Rotating from NGINX -> HTTPD")
            self.container_controller.create_container(HTTPD.lower())
            self.port_controller.swap_to_container(HTTPD)
            self.container_controller.remove_container(old_container)
            container = HTTPD
        elif self.container_controller.active_container.name == HTTPD.lower():
            logger.info("Rotating from HTTPD -> NGINX")
            self.container_controller.create_container(NGINX.lower())
            self.port_controller.swap_to_container(NGINX)
            self.container_controller.remove_container(old_container)
            container = NGINX
        else:
            logger.error(f"MTD rotation failed cause of: {str(e)}")
            raise ValueError(f"MTD rotation failed cause of: {str(e)}")
    
    def start(self):
        ini_time = time.time()
        end_time = ini_time + self.duration
        try:
            while time.time() < end_time and not get_shutdown():
                wait_time = random.uniform(self.lower, self.upper)
                logger.debug(f"{wait_time:.2f}s until the next swap...")
                time.sleep(wait_time)
                if get_shutdown():
                    break
                self.switch()

        except Exception as e:
            logger.error(str(e))
            raise ValueError(f"Error in the MTD loop: {str(e)}")
