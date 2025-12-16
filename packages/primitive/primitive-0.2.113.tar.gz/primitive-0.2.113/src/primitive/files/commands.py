import json
import typing
from pathlib import Path

import click
from loguru import logger

from primitive.files.ui import render_files_table

from ..utils.printer import print_result

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.group("files")
@click.pass_context
def cli(context):
    """Files"""
    pass


@cli.command("upload")
@click.pass_context
@click.argument("path", type=click.Path(exists=True))
@click.option("--public", "-p", help="Is this a Public file", is_flag=True)
@click.option("--key-prefix", "-k", help="Key Prefix", default="")
@click.option("--direct", help="direct", is_flag=True)
def file_upload_command(context, path, public, key_prefix, direct):
    """File Upload"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    path = Path(path)
    try:
        if direct:
            result = primitive.files.upload_file_direct(
                path, is_public=public, key_prefix=key_prefix
            )
        else:
            result = primitive.files.upload_file_via_api(
                path, is_public=public, key_prefix=key_prefix
            )
        message = json.dumps(result.json())
    except AttributeError:
        message = "File Upload Failed"
    except Exception as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(error)
            context.exit(1)

    print_result(message=message, context=context)


@cli.command("download")
@click.pass_context
@click.option("--file-id", help="File ID", required=False)
@click.option("--file-name", help="File Name", required=False)
@click.option("--output", help="Output Path", required=False, type=click.Path())
@click.option("--organization-id", help="Organization ID", required=False)
@click.option("--organization", help="Organization Slug", required=False)
def file_download_command(
    context,
    file_id=None,
    file_name=None,
    output=None,
    organization_id=None,
    organization=None,
):
    """File Download"""
    primitive: Primitive = context.obj.get("PRIMITIVE")

    if not file_id and not file_name:
        raise click.UsageError("Either --id or --file-name must be provided.")

    if not output:
        output = Path().cwd()
    else:
        output = Path(output)

    downloaded_file = primitive.files.download_file(
        output_path=output,
        file_id=file_id,
        file_name=file_name,
        organization_id=organization_id,
        organization_slug=organization,
    )
    print_result(message=f"File downloaded to {downloaded_file}", context=context)


@cli.command("list")
@click.pass_context
@click.option("--organization-id", help="Organization ID", required=False)
@click.option("--organization", help="Organization Slug", required=False)
def list_command(context, organization_id=None, organization=None):
    """List Files"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    files_result = primitive.files.files(
        organization_id=organization_id, organization_slug=organization
    )

    files = [file.get("node") for file in files_result.data.get("files").get("edges")]

    if context.obj["JSON"]:
        print_result(message=files, context=context)
    else:
        render_files_table(files)
