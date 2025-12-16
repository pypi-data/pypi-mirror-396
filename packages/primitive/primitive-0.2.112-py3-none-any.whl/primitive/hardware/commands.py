from time import sleep
from typing import TYPE_CHECKING, Optional

import click
from loguru import logger
from primitive.utils.printer import print_result
from primitive.hardware.ui import render_hardware_table
from primitive.utils.x509 import (
    generate_csr_pem,
    write_certificate_pem,
)

if TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Hardware"""
    pass


@cli.command("systeminfo")
@click.option(
    "--with-installed-applications",
    is_flag=True,
    default=False,
    help="Only for MacOS, list installed applications using metadata commands",
)
@click.pass_context
def systeminfo_command(
    context,
    with_installed_applications: bool = False,
):
    """Get System Info"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    message = primitive.hardware.get_system_info(
        with_installed_applications=with_installed_applications
    )
    print_result(message=message, context=context)


@cli.command("register")
@click.option(
    "--organization",
    type=str,
    help="Organization [slug] to register hardware with",
)
@click.option(
    "--issue-certificate",
    is_flag=True,
    show_default=True,
    default=False,
    help="Issue certificate.",
)
@click.pass_context
def register_command(
    context, organization: Optional[str] = None, issue_certificate: bool = False
):
    """Register Hardware with Primitive"""
    primitive: Primitive = context.obj.get("PRIMITIVE")

    organization_id = None
    if organization:
        organization_data = primitive.organizations.get_organization(slug=organization)
        organization_id = organization_data.get("id")

    if not organization_id:
        logger.info("Registering hardware with the default organization.")

    result = primitive.hardware.register(organization_id=organization_id)
    hardware = result.data.get("registerHardware")

    if not hardware:
        print_result(
            fg="red",
            context=context,
            message="There was an error registering this device. Please review the above logs.",
        )
        return

    if issue_certificate:
        certificate = primitive.hardware.certificate_create(
            hardware_id=hardware["id"],
            csr_pem=generate_csr_pem(
                hardware_id=hardware["pk"],
            ),
        )
        write_certificate_pem(certificate.certificate_pem)

    print_result(
        fg="green",
        context=context,
        message="Hardware registered successfully.",
    )


@cli.command("unregister")
@click.pass_context
def unregister_command(context):
    """Unregister Hardware with Primitive"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    result = primitive.hardware.unregister()
    color = "green" if result else "red"
    if not result:
        message = "There was an error unregistering this device. Please review the above logs."
        return
    elif result.data.get("unregisterHardware"):
        message = "Hardware unregistered successfully"
    print_result(message=message, context=context, fg=color)


@cli.command("checkin")
@click.option(
    "--http",
    is_flag=True,
    default=False,
    help="Use HTTP instead of amqp for check-in",
)
@click.pass_context
def checkin_command(context, http: bool = False):
    """Checkin Hardware with Primitive"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    primitive.hardware.check_in(http=http)


@cli.command("list")
@click.pass_context
def list_command(context):
    """List Hardware"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    get_hardware_list_result = primitive.hardware.get_hardware_list(
        nested_children=True
    )

    hardware_list = [
        hardware.get("node")
        for hardware in get_hardware_list_result.data.get("hardwareList").get("edges")
    ]

    if context.obj["JSON"]:
        print_result(message=hardware_list, context=context)
        return
    else:
        render_hardware_table(hardware_list)


@cli.command("get")
@click.pass_context
@click.argument(
    "hardware_identifier",
    type=str,
    required=True,
)
def get_command(context, hardware_identifier: str) -> None:
    """Get Hardware"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    hardware = primitive.hardware.get_hardware_from_slug_or_id(
        hardware_identifier=hardware_identifier
    )

    if context.obj["JSON"]:
        print_result(message=hardware, context=context)
        return
    else:
        render_hardware_table([hardware])


@cli.command("metrics")
@click.pass_context
@click.option("--watch", is_flag=True, help="Watch hardware metrics")
def metrics_command(context, watch: bool = False) -> None:
    """Get Hardware Metrics"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    if watch:
        while True:
            print_result(message=primitive.hardware.get_metrics(), context=context)
            sleep(1)
    else:
        print_result(message=primitive.hardware.get_metrics(), context=context)


@cli.command("bmc")
@click.pass_context
@click.argument(
    "hardware_identifier",
    type=str,
    required=True,
)
@click.option(
    "--hostname-override",
    type=str,
    default=None,
    help="Override the hostname or IP address used to connect to the BMC. If you are on VLAN you can use this to specify a host's IP that is not registered in Primitive.",
)
def bmc(
    context, hardware_identifier: str, hostname_override: Optional[str] = None
) -> None:
    """Start BMC Tunnel"""
    primitive: Primitive = context.obj.get("PRIMITIVE")

    primitive.hardware.start_bmc_tunnel(
        hardware_identifier=hardware_identifier, hostname_override=hostname_override
    )
