import pydbus
from .decorators import apply_timing_to_methods, timing_decorator
from .config import PORT, NGINX, HTTPD, PROXY, logger

TCP = "tcp"
UDP = "udp"

@apply_timing_to_methods(timing_decorator)
class PortController:
    def __init__(self, running=NGINX):
        bus = pydbus.SystemBus()

        # Connect with the firewalld service via D-Bus
        self.firebus = bus.get('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1')
        self.zone = self.firebus.getDefaultZone()

        self.init_masquerade = self.firebus.queryMasquerade(self.zone)
        if not self.init_masquerade:
            self.firebus.addMasquerade(self.zone, 0)

        self.init_ports = self.__get_ports()
        self.__add_port(running, TCP)
        self.__add_port(running, UDP)

        rest = [NGINX, HTTPD]       
        rest.remove(running)
        
        # Deletes the ports related to others containers if they exists
        for container in rest:
            self.__remove_port(container, UDP)
            self.__remove_port(container, TCP)

    def close(self):
        try:
            self.__recover_masquerade()
            self.__recover_ports()
        except Exception as e:
            logger.error(f"Closing the port controller: {str(e)}")
    
    def __recover_masquerade(self):
        if self.firebus.queryMasquerade(self.zone) and not self.init_masquerade:
            self.firebus.removeMasquerade(self.zone, 0)
        elif not self.firebus.queryMasquerade(self.zone) and self.init_masquerade:
            self.firebus.addMasquerade(self.zone, 0)

    def __recover_ports(self):
        for container, protocols in self.init_ports.items():
            for protocol in protocols:
                if protocol:
                    self.__add_port(container, protocol)
                else:
                    self.__remove_port(container, protocol)

    def swap_to_container(self, container):
        if container == NGINX:
            self.__remove_port(HTTPD, UDP)
            self.__remove_port(HTTPD, TCP)
            self.__add_port(NGINX, UDP)
            self.__add_port(NGINX, TCP)
            logger.info(f"Forwardind port changed from {PORT[HTTPD]} -> {PORT[NGINX]}")
        else:
            self.__remove_port(NGINX, UDP)
            self.__remove_port(NGINX, TCP)
            self.__add_port(HTTPD, UDP)
            self.__add_port(HTTPD, TCP)
            logger.info(f"Forwardind port changed from {PORT[NGINX]} -> {PORT[HTTPD]}")
            
    def __remove_port(self, container, protocol):
        try:
            self.firebus.removeForwardPort('', PORT[PROXY], protocol, PORT[container], '')
        except Exception as e:
            if 'g-io-error-quark: GDBus.Error:org.fedoraproject.FirewallD1.Exception: NOT_ENABLED:' in str(e):
                pass
            else:
                logger.error(f"The port could not be deleted: {str(e)}")

    def __add_port(self, container, protocol):
        try:
            self.firebus.addForwardPort('', PORT[PROXY], protocol, PORT[container], '', 0)
        except Exception as e:
            if 'GDBus.Error:org.fedoraproject.FirewallD1.Exception: ALREADY_ENABLED' in str(e):
                pass
            else:
                logger.error(f"The port could not be added: {str(e)}")

    def __get_ports(self):
        ports = {NGINX:{}, HTTPD:{}}
        f_ports = self.firebus.getForwardPorts(self.zone)
        for container in (NGINX, HTTPD):
            for protocol in (TCP, UDP):
                if [PORT[PROXY], protocol, PORT[container], ''] in f_ports:
                    ports[container][protocol] = True
                else:
                    ports[container][protocol] = False
        return ports
