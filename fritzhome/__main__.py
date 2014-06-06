"""
    FRITZ!Box SmartHome Client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


from __future__ import print_function, division

import re
import time
import socket

import click

from .fritz import FritzBox


@click.group()
@click.option('--host', default='fritz.box')
@click.option('--username', default='smarthome')
@click.option('--password', default='smarthome')
@click.pass_context
def cli(context, host, username, password):
    """
    FritzBox SmartHome Tool

    \b
    Provides the following functions:
    - A easy to use library for querying SmartHome actors
    - This CLI tool for testing
    - A carbon client for pipeing data into graphite
    """
    context.obj = FritzBox(host, username, password)


@cli.command()
@click.pass_context
def energy(context):
    """Display energy stats of all actors"""
    fritz = context.obj
    fritz.login()

    for actor in fritz.get_actors():
        click.echo("{} ({}): {:.2f} Watt current, {:.3f} wH total".format(
            actor.name,
            actor.actor_id,
            actor.get_power() / 1000,
            actor.get_energy() / 100
        ))


@cli.command()
@click.argument('server')
@click.option('--port', type=int, default=2003)
@click.option('--interval', type=int, default=10)
@click.option('--prefix', default="smarthome")
@click.pass_context
def graphite(context, server, port, interval, prefix):
    """Display energy stats of all actors"""
    fritz = context.obj
    fritz.login()
    sid_ttl = time.time() + 600

    # Find actors and create carbon keys
    click.echo(" * Requesting actors list")
    simple_chars = re.compile('[^A-Za-z0-9]+')
    actors = fritz.get_actors()
    keys = {}
    for actor in actors:
        keys[actor.name] = "{}.{}".format(
            prefix,
            simple_chars.sub('_', actor.name)
        )

    # Connect to carbon
    click.echo(" * Trying to connect to carbon")
    timeout = 2
    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect((server, port))
    except socket.timeout:
        raise Exception("Took over {} second(s) to connect to {}".format(
            timeout, server
        ))
    except Exception as error:
        raise Exception("unknown exception while connecting to {} - {}".format(
            server, error
        ))

    def send(key, value):
        """Send a key-value-pair to carbon"""
        now = int(time.time())
        payload = "{} {} {}\n".format(key, value, now)
        sock.sendall(payload)

    while True:
        if time.time() > sid_ttl:
            click.echo(" * Requesting new SID")
            fritz.login()
            sid_ttl = time.time() + 600

        click.echo(" * Requesting statistics")
        for actor in actors:
            power = actor.get_power()
            total = actor.get_energy()
            click.echo("   -> {}: {:.2f} Watt current, {:.3f} wH total".format(
                actor.name, power / 1000, total / 100
            ))

            send(keys[actor.name] + '.current', power)
            send(keys[actor.name] + '.total', total)

        time.sleep(interval)


@cli.command(name="switch-on")
@click.argument('ain')
@click.pass_context
def switch_on(context, ain):
    """Switch an actor's power to ON"""
    context.obj.login()
    actor = context.obj.get_actor_by_ain(ain)
    if actor:
        click.echo("Switching {} on".format(actor.name))
        actor.switch_on()
    else:
        click.echo("Actor not found: {}".format(ain))


@cli.command(name="switch-off")
@click.argument('ain')
@click.pass_context
def switch_off(context, ain):
    """Switch an actor's power to OFF"""
    context.obj.login()
    actor = context.obj.get_actor_by_ain(ain)
    if actor:
        click.echo("Switching {} off".format(actor.name))
        actor.switch_off()
    else:
        click.echo("Actor not found: {}".format(ain))


if __name__ == '__main__':
    cli()
