import os
import docker
from behave import given, when, then, use_step_matcher
import unittest
from mass.container_controller import ContainerController
from mass.config import NGINX, HTTPD, PROXY, PORT
from common.helpers import *
import re


@given('I have a running docker service')
def step_check_firewalld_running(context):
    import subprocess
    result = subprocess.run(['docker', 'ps'])
    unittest.TestCase().assertEqual(result.returncode, 0, "docker is not running")
    context.running = []


@when('I create a ContainerController with a {container} container')
def step_create_container_controller(context, container):
    context.container_controller = ContainerController(container)


@then('the {container} container should be running')
def step_check_container_creation_succeeded(context, container):
    running = get_container(container)
    unittest.TestCase().assertEqual(running.status, 'running')
    context.running.append(running)
    if len(context.running) > 1:
        unittest.TestCase().assertNotEqual(context.running[0], context.running[1])

@when('closing the ContainerController')
def closing_container(context):
    context.container_controller.close()

@then('the {container} container should not be running')
def step_container_should_not_be_running(context, container):
    for cnt in get_containers():
        if cnt.name is container:
            # Corner case when two container with the same name are created,
            # in that case is needed to check the objects directly.
            for running_container in context.running:
                if running_container.name is container:
                    unittest.TestCase().assertNotEqual(cnt, running_container)

@when('I create a {container} container')
def step_when_i_create_a_container(context, container):
    context.container_controller.create_container(container)


@when('I remove the {container} container')
def step_when_i_remove_the_container(context, container):
    context.container_controller.remove_container(get_container(container))

@then(u'there should be no containers running')
def step_container_not_running(context):
    unittest.TestCase().assertFalse(get_containers())
