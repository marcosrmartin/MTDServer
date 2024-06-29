import os
import time
import signal
import asyncio
import unittest
from common.helpers import * 
from behave import when, then, given
from behave.api.async_step import async_run_until_complete, use_or_create_async_context, AsyncContext

from features.steps.container_controller_steps import *
from features.steps.port_controller_steps import *
from mass import MTDController

@when('I create a MTDController with {duration} duration, {lower} lower and {upper} upper')
def step_create_mtd_controller(context, duration, lower, upper):
    context.masquerade = get_masquerade()
    context.ports = sorted(get_ports())
    try:
        context.mtd = MTDController(int(duration), int(lower), int(upper))
        context.mtd_error = None
    except Exception as e:
        context.mtd_error = e

@then('the MTD should be created correctly')
def step_check_mtd_created(context):
    unittest.TestCase().assertFalse(context.mtd_error)
    step_check_initial_masquerade(context)
    step_check_ports_added(context, 'NGINX')
    step_check_container_creation_succeeded(context, 'nginx')

@then('the MTD creation should fail')
def step_check_mtd_created(context):
    unittest.TestCase().assertIsNotNone(context.mtd_error, "Expected a ValueError but no error was raised")
    unittest.TestCase().assertIsInstance(context.mtd_error, ValueError, f"Expected ValueError but got {type(context.mtd_error).__name__}")
    unittest.TestCase().assertEqual(context.mtd_error.args[0], f"The lower bound cannot be higher than the upper bound.")

@when('the MTD is started')
def step_start_mtd(context):
    try:
        context.mtd.start()
        context.mtd_runinng_error = None
    except Exception as e:
        context.mtd_runinng_error = e


async def step_async_mtd_run(mtd):
    try:
        await mtd.start()
    except Exception as e:
        return e


@when('the MTD is started asynchronously')
def step_asynnc(context):
    async_context = use_or_create_async_context(context, "async_context")
    task = async_context.loop.create_task(step_async_mtd_run(context.mtd))
    async_context.tasks.append(task)


@then('the running should stop')
def step_check_mtd_stop(context):
    async_context = context.async_context
    done, pending = async_context.loop.run_until_complete(
        asyncio.wait(async_context.tasks))

    parts = [task.result() for task in done]

    unittest.TestCase().assertIsNotNone(parts[0], "Expected a ValueError but no error was raised")
    unittest.TestCase().assertIsInstance(parts[0], ValueError, f"Expected ValueError but got {type(context.mtd_error).__name__}")
    unittest.TestCase().assertEqual(parts[0].args[0], f"Error in the MTD loop: MTD run stopped by user.")

@when('I press crtl+c')
def step_stop_mtd_run(context):
    time.sleep(10)
    os.kill(os.getpid(), signal.SIGINT)


@then('the running should be successful')
def step_check_mtd_run(context):
    unittest.TestCase().assertIsNone(context.mtd_runinng_error)

@when('I close the MTD')
def step_mtd_closing(context):
    context.mtd.close()
