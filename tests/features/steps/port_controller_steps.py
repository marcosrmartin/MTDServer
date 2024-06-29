import unittest
from behave import when, then, given, use_step_matcher
from mass import PortController, NGINX, HTTPD, PORT, PROXY
from common.helpers import *
import re

@given('I have a running firewalld service')
def step_check_firewalld_running(context):
    import subprocess
    result = subprocess.run(['systemctl', 'is-active', '--quiet', 'firewalld'])
    unittest.TestCase().assertEqual(result.returncode, 0, "firewalld is not running")

@given('the masquerade {enable}')
def step_set_masquerade(context, enable):
    set_masquerade(int(enable))

@given('the ports {nginx_udp}, {nginx_tcp}, {httpd_udp}, {httpd_tcp}')
def step_set_ports(context, nginx_udp, nginx_tcp, httpd_udp, httpd_tcp):
    set_ports(int(nginx_udp), int(nginx_tcp), int(httpd_udp), int(httpd_tcp))

@when('I create a PortController with the {container_port} container port')
def step_create_port_controller(context, container_port):
    context.masquerade = get_masquerade()
    context.ports = sorted(get_ports())
    try:
        context.port_controller = PortController(running=container_port)
        context.error = None
    except Exception as e:
        context.error = e
        context.container_port = container_port

@then('it should succeed')
def step_check_port_controller_creation_succeeded(context):
    unittest.TestCase().assertIsNone(context.error, f"PortController error: {context.error}")

@then('it should fail')
def step_check_creation_failed_with_valueerror(context):
    unittest.TestCase().assertIsNotNone(context.error, "Expected a ValueError but no error was raised")
    unittest.TestCase().assertIsInstance(context.error, ValueError, f"Expected ValueError but got {type(context.error).__name__}")
    unittest.TestCase().assertEqual(context.error.args[0], f"The forwarding port must match a exposed container port [{NGINX}, {HTTPD}].")

@then('the masquerade should be enabled')
def step_check_initial_masquerade(context):
    masquerade = get_masquerade()
    unittest.TestCase().assertTrue(masquerade, "The masquerade is not enabled")

@then('the {container_port} port for the running container should be added')
def step_check_ports_added(context, container_port):
    expected_ports = [
        [PORT[PROXY], 'tcp', PORT[container_port], ''],
        [PORT[PROXY], 'udp', PORT[container_port], '']
    ]
    unittest.TestCase().assertEqual(sorted(get_ports()), expected_ports)

@then('the {container_port} port for the old container should be removed')
def step_check_ports_removed_nginx(context, container_port):
    expected_ports = [
        [PORT[PROXY], 'tcp', PORT[container_port], ''],
        [PORT[PROXY], 'udp', PORT[container_port], '']
    ]
    unittest.TestCase().assertNotEqual(sorted(get_ports()), expected_ports)

@when('Rotating to {new_container}')
def swap(context, new_container):
    try:
        context.port_controller.swap_to_container(new_container)
        context.error = None
    except Exception as e:
        context.error = e
        context.container_port = new_container

@when('closing the controller')
def closing(context):
    context.port_controller.close()


@then('the firewall configuration should be the same as the start of the scenario')
def step_check_restored(context):
    unittest.TestCase().assertEqual(sorted(get_ports()), context.ports)
    unittest.TestCase().assertEqual(get_masquerade(), context.masquerade)
