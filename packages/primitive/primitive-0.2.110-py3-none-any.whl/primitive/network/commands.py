from typing import TYPE_CHECKING

import click
from primitive.utils.printer import print_result
from primitive.network.ui import render_ports_table

if TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Network"""
    pass


@cli.command("switch")
@click.pass_context
def switch(context):
    """Switch"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    switch_info = primitive.network.get_switch_info()
    if context.obj["JSON"]:
        message = switch_info
    else:
        message = f"Vendor: {switch_info.get('vendor')}. Model: {switch_info.get('model')}. IP: {switch_info.get('ip_address')}"
    print_result(message=message, context=context)


@cli.command("interfaces")
@click.pass_context
@click.option(
    "--push",
    is_flag=True,
    show_default=True,
    default=False,
    help="Push current interface info.",
)
def interfaces(context, push: bool = False):
    """Interfaces"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    interfaces_info = primitive.network.get_interfaces_info()
    if push:
        primitive.network.push_switch_and_interfaces_info(
            interfaces_info=interfaces_info
        )
    if context.obj["JSON"]:
        print_result(message=interfaces_info, context=context)
    else:
        render_ports_table(interfaces_info)
