# coding: utf-8
"""
    FRITZ!Box SmartHome Client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


from __future__ import print_function, division

import re
import time
import json
import socket

import click

from .fritz import FritzBox


@click.group()
@click.option('--host', default='169.254.1.1') # fritzbox "emergency" IP
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
def actors(context):
    """Display a list of actors"""
    fritz = context.obj
    fritz.login()

    for actor in fritz.get_actors():
        click.echo("{} ({} {}; AIN {})".format(
            actor.name,
            actor.manufacturer,
            actor.productname,
            actor.actor_id,
        ))


@cli.command()
@click.option('--features', type=bool, default=False, help="Show device features")
@click.pass_context
def energy(context, features):
    """Display energy stats of all actors"""
    fritz = context.obj
    fritz.login()

    for actor in fritz.get_actors():
        click.echo("{} ({}): {:.2f} Watt current, {:.3f} wH total, {:.2f} °C".format(
            actor.name,
            actor.actor_id,
            (actor.get_power() or 0.0) / 1000,
            (actor.get_energy() or 0.0) / 100,
            actor.temperature
        ))
        if features:
            click.echo("  Features: PowerMeter: {}, Temperatur: {}, Switch: {}".format(
                actor.has_powermeter, actor.has_temperature, actor.has_switch
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


@cli.command(name="switch-state")
@click.argument('ain')
@click.pass_context
def switch_state(context, ain):
    """Get an actor's power state"""
    context.obj.login()
    actor = context.obj.get_actor_by_ain(ain)
    if actor:
        click.echo("State for {} is: {}".format(ain,'ON' if actor.get_state() else 'OFF'))
    else:
        click.echo("Actor not found: {}".format(ain))


@cli.command(name="switch-toggle")
@click.argument('ain')
@click.pass_context
def switch_toggle(context, ain):
    """Toggle an actor's power state"""
    context.obj.login()
    actor = context.obj.get_actor_by_ain(ain)
    if actor:
        if actor.get_state():
            actor.switch_off()
            click.echo("State for {} is now OFF".format(ain))
        else:
            actor.switch_on()
            click.echo("State for {} is now ON".format(ain))
    else:
        click.echo("Actor not found: {}".format(ain))


@cli.command()
@click.option('--format', type=click.Choice(['plain', 'json']),
              default='plain')
@click.pass_context
def logs(context, format):
    """Show system logs since last reboot"""
    fritz = context.obj
    fritz.login()

    messages = fritz.get_logs()
    if format == "plain":
        for msg in messages:
            merged = "{} {} {}".format(msg.date, msg.time, msg.message.encode("UTF-8"))
            click.echo(merged)

    if format == "json":
        entries = [msg._asdict() for msg in messages]
        click.echo(json.dumps({
            "entries": entries,
        }))


if __name__ == '__main__':
    cli()
