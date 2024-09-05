import time
import random
from .config import NGINX, HTTPD, logger, get_shutdown
from .container_controller import ContainerController
from .port_controller import PortController

class MTDController:
    def __init__(self, duration, lower, upper):
        if type(duration) is not int:
            raise ValueError("The duration arg is not int.")
        elif duration < 0:
            raise ValueError("The duration ag is not rint.")
        if type(lower) is not int:
            raise ValueError("The lower arg is not int.")
        if type(upper) is not int:
            raise ValueError("The upper arg is not int.")
        
        if duration < 0 or lower < 0 or upper < 0:
            raise ValueError("The value cannot be negative.")

        if lower > upper:
            logger.error("The lower bound cannot be higher than the upper bound.")
            raise ValueError("The lower bound cannot be higher than the upper bound.")
        
        self._container_controller = ContainerController()
        self._port_controller = PortController()
        self._duration = duration
        self._lower = lower
        self._upper = upper

    def close(self):
        self._container_controller.close()
        self._port_controller.close()

    def __switch(self):
        current_container = self._container_controller.get_current_container()
        if current_container.name == NGINX.lower():
            logger.info("Rotating from NGINX -> HTTPD")
            self._container_controller.create_container(HTTPD.lower())
            self._port_controller.swap_to_container(HTTPD)
            self._container_controller.remove_container(current_container)
        elif current_container.name == HTTPD.lower():
            logger.info("Rotating from HTTPD -> NGINX")
            self._container_controller.create_container(NGINX.lower())
            self._port_controller.swap_to_container(NGINX)
            self._container_controller.remove_container(current_container)
        else:
            logger.error(f"MTD rotation failed cause of: {str(e)}")
            raise ValueError(f"MTD rotation failed cause of: {str(e)}")
    
    def start(self):
        ini_time = time.time()
        end_time = ini_time + self._duration
        try:
            logger.info(f"Runnning with: duration: {self._duration}, lower: {self._lower}, upper: {self._upper}")

            while time.time() < end_time and not get_shutdown():
                wait_time = random.uniform(self._lower, self._upper)
                logger.debug(f"{wait_time:.2f}s until the next swap...")
                time.sleep(wait_time)
                if get_shutdown():
                    break
                self.__switch()
            if get_shutdown():
                logger.error('MTD run stopped by user')
                # raise ValueError(f"MTD run stopped by user.")
            return True
        except Exception as e:
            logger.error(str(e))
            raise ValueError(f"Error in the MTD loop: {str(e)}")
