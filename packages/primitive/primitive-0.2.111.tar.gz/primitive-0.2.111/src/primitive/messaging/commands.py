import click


import typing

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Messaging Commands"""
    pass


@cli.command("test-message")
@click.pass_context
def test_message(context):
    """Send Test Message"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    primitive.messaging.send_test_event()
