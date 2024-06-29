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
        self._firebus = bus.get('org.fedoraproject.FirewallD1', '/org/fedoraproject/FirewallD1')
        self._zone = self._firebus.getDefaultZone()

        self._init_masquerade = self._firebus.queryMasquerade(self._zone)
        if not self._init_masquerade:
            self._firebus.addMasquerade(self._zone, 0)

        self._init_ports = self.__get_ports()
        self.__add_port(running, TCP)
        self.__add_port(running, UDP)

        if running not in (NGINX, HTTPD):
            raise ValueError(f"The forwarding port must match a exposed container port [{NGINX}, {HTTPD}].")

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
        if self._firebus.queryMasquerade(self._zone) and not self._init_masquerade:
            self._firebus.removeMasquerade(self._zone)
        elif not self._firebus.queryMasquerade(self._zone) and self._init_masquerade:
            self._firebus.addMasquerade(self._zone, 0)

    def __recover_ports(self):
        for container, protocols in self._init_ports.items():
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
        elif container == HTTPD:
            self.__remove_port(NGINX, UDP)
            self.__remove_port(NGINX, TCP)
            self.__add_port(HTTPD, UDP)
            self.__add_port(HTTPD, TCP)
            logger.info(f"Forwardind port changed from {PORT[NGINX]} -> {PORT[HTTPD]}")
        else:
            raise ValueError(f"Only [{NGINX}, {HTTPD}] are available when swapping.")
            
    def __remove_port(self, container, protocol):
        try:
            self._firebus.removeForwardPort('', PORT[PROXY], protocol, PORT[container], '')
        except Exception as e:
            if 'g-io-error-quark: GDBus.Error:org.fedoraproject.FirewallD1.Exception: NOT_ENABLED:' in str(e):
                pass
            else:
                logger.error(f"The port could not be deleted: {str(e)}")

    def __add_port(self, container, protocol):
        try:
            self._firebus.addForwardPort('', PORT[PROXY], protocol, PORT[container], '', 0)
        except Exception as e:
            if 'GDBus.Error:org.fedoraproject.FirewallD1.Exception: ALREADY_ENABLED' in str(e):
                pass
            else:
                logger.error(f"The port could not be added: {str(e)}")

    def __get_ports(self):
        ports = {NGINX:{}, HTTPD:{}}
        f_ports = self._firebus.getForwardPorts(self._zone)
        for container in (NGINX, HTTPD):
            for protocol in (TCP, UDP):
                if [PORT[PROXY], protocol, PORT[container], ''] in f_ports:
                    ports[container][protocol] = True
                else:
                    ports[container][protocol] = False
        return ports
