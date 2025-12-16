from pathlib import Path
import click
import typing

from loguru import logger
from primitive.utils.cache import get_operating_systems_cache
from .exceptions import P_CLI_200, P_CLI_201

if typing.TYPE_CHECKING:
    from ..client import Primitive


@click.group("operating-systems")
@click.pass_context
def cli(context):
    "Operating Systems"
    pass


@cli.command("list")
@click.option(
    "--organization-slug",
    help="Organization slug to list operating systems for",
    required=False,
)
@click.pass_context
def operating_systems_list_command(context, organization_slug):
    primitive: Primitive = context.obj.get("PRIMITIVE")

    organization = (
        primitive.organizations.get_organization(slug=organization_slug)
        if organization_slug
        else primitive.organizations.get_default_organization()
    )

    if not organization:
        if organization_slug:
            logger.error(f"No organization found with slug {organization_slug}")
        else:
            logger.error("Failed to fetch default organization")

    operating_systems = primitive.operating_systems.list(
        organization_id=organization["id"]
    )
    operating_system_slugs = [
        operating_system["slug"] for operating_system in operating_systems
    ]

    newline = "\n"
    logger.info(
        f"Operating systems: {newline}- {f'{newline}- '.join(operating_system_slugs)}"
    )


@cli.command("create")
@click.option("--slug", help="Slug for created operating system", required=True)
@click.option(
    "--iso-file", help="Path to operating system iso file to upload", required=True
)
@click.option(
    "--checksum-file",
    help="Path to operating system checksum file to upload",
    required=True,
)
@click.option(
    "--checksum-file-type", help="The type of the checksum file", required=True
)
@click.option(
    "--organization-slug",
    help="Organization to create the operating system in",
    required=False,
)
@click.option(
    "--is-global",
    help="[ADMIN] Create global operating system",
    is_flag=True,
    hidden=True,
)
@click.pass_context
def create_command(
    context,
    slug,
    iso_file,
    checksum_file,
    checksum_file_type,
    organization_slug,
    is_global,
):
    primitive: Primitive = context.obj.get("PRIMITIVE")

    if organization_slug:
        organization = primitive.organizations.get_organization(slug=organization_slug)
    else:
        organization = primitive.organizations.get_default_organization()

    if not organization:
        if organization_slug:
            logger.error(f"No organization found with slug {organization_slug}")
            return
        else:
            logger.error("Failed to fetch default organization")
            return

    try:
        primitive.operating_systems.create(
            slug=slug,
            iso_file=iso_file,
            checksum_file=checksum_file,
            checksum_file_type=checksum_file_type,
            organization_id=organization["id"],
            is_global=is_global,
        )
    except P_CLI_200:
        logger.info(
            f"Operating system with slug {slug} already exists, skipping creation."
        )
        return
    except Exception as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(error)
            context.exit(1)

    logger.success("Operating system created in primitive.")


@cli.command("delete")
@click.argument("operating-system-identifier")
@click.option("--organization-slug", help="Organization slug", required=False)
@click.option(
    "--is-global",
    help="[ADMIN] Create global operating system",
    is_flag=True,
    hidden=True,
)
@click.pass_context
def delete(
    context,
    operating_system_identifier,
    organization_slug,
    is_global,
):
    primitive: Primitive = context.obj.get("PRIMITIVE")

    if organization_slug:
        organization = primitive.organizations.get_organization(slug=organization_slug)
    else:
        organization = primitive.organizations.get_default_organization()

    if not organization:
        if organization_slug:
            logger.error(f"No organization found with slug {organization_slug}")
            return
        else:
            logger.error("Failed to fetch default organization")
            return

    identifier_info = primitive.operating_systems.get_slug_or_id(
        operating_system_identifier=operating_system_identifier
    )

    base64_id = operating_system_identifier if identifier_info.get("id") else None

    try:
        delete_result = primitive.operating_systems.delete(
            id=base64_id,
            slug=identifier_info.get("slug"),
            is_global=is_global,
            organization_id=organization["id"],
        )
    except P_CLI_201 as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(
                f"No operating system found with identifier {operating_system_identifier}"
            )
            context.exit(1)
    except Exception as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(error)
            context.exit(1)

    slug = delete_result.get("slug")

    if not slug:
        logger.error("Failed to delete operating system")
        return

    try:
        primitive.operating_systems.uncache(operating_system_name=slug)
    except FileNotFoundError:
        logger.warning(f"Operating system {slug} not found in cache")
    except Exception as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(error)
            context.exit(1)

    logger.success("Operating system deleted")


@cli.command("download")
@click.argument("operating-system-identifier", required=False)
@click.option("--id", help="Operating system ID", required=False)
@click.option("--slug", help="Operating system slug", required=False)
@click.option("--organization-slug", help="Organization slug", required=False)
@click.option(
    "--directory",
    help="Directory to download the operating system files to",
    required=False,
)
@click.option(
    "--overwrite",
    help="Overwrite existing files if they exist",
    is_flag=True,
    required=False,
)
@click.pass_context
def download(
    context,
    operating_system_identifier,
    id,
    slug,
    organization_slug,
    directory,
    overwrite,
):
    if not (operating_system_identifier or id or slug):
        raise click.UsageError(
            "You must provide either a string or specific --id or --slug."
        )
    if operating_system_identifier and id and slug:
        raise click.UsageError(
            "You can only specify one of operating_system_identifier, --id or --slug."
        )

    primitive: Primitive = context.obj.get("PRIMITIVE")
    if operating_system_identifier and not (id or slug):
        identifier_info = primitive.operating_systems.get_slug_or_id(
            operating_system_identifier
        )
        id = identifier_info.get("id", None)
        slug = identifier_info.get("slug", None)

    organization = (
        primitive.organizations.get_organization(slug=organization_slug)
        if organization_slug
        else primitive.organizations.get_default_organization()
    )

    if not organization:
        if organization_slug:
            logger.error(f"No organization found with slug {organization_slug}")
            return
        else:
            logger.error("Failed to fetch default organization")
            return

    try:
        operating_system_directory = primitive.operating_systems.download(
            id=id,
            slug=slug,
            organization_id=organization["id"],
            directory=directory,
            overwrite=overwrite,
        )
    except Exception as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(error)
            context.exit(1)

    logger.success(
        f"Successfully downloaded operating system to {operating_system_directory}"
    )


@cli.command("uncache", help="Remove the operating system from the local cache")
@click.pass_context
@click.argument("operating-system")
def uncache(context, operating_system):
    primitive: Primitive = context.obj.get("PRIMITIVE")

    try:
        primitive.operating_systems.uncache(operating_system_name=operating_system)
    except FileNotFoundError as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(f"Operating system {operating_system} not found in cache")
            context.exit(1)
    except Exception as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(error)
            context.exit(1)

    logger.info(f"Operating system {operating_system} removed from cache")


@cli.group("remotes")
@click.pass_context
def remotes(context):
    "Remotes"
    pass


@remotes.command("download")
@click.pass_context
@click.argument("operating-system")
@click.option(
    "--directory",
    help="Directory to download the operating system files to",
    required=False,
)
def operating_system_remotes_download_command(
    context, operating_system, directory=None
):
    primitive: Primitive = context.obj.get("PRIMITIVE")

    try:
        primitive.operating_systems.download_remote(
            remote_operating_system_name=operating_system, directory=directory
        )
    except Exception as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(error)
            context.exit(1)

    cache_directory = Path(directory) if directory else get_operating_systems_cache()
    operating_system_directory = cache_directory / operating_system

    logger.success(
        f"Successfully downloaded operating system files to {operating_system_directory}"
    )


@remotes.command("mirror")
@click.pass_context
@click.argument("operating-system")
@click.option("--slug", help="Slug of the operating system", required=False)
@click.option(
    "--organization-slug",
    help="Slug of the organization to upload the operating system to",
    required=False,
)
@click.option(
    "--directory",
    help="Directory to download the operating system files to",
    required=False,
)
@click.option(
    "--is-global",
    help="[ADMIN] Create global operating system",
    is_flag=True,
    hidden=True,
)
@click.option(
    "--overwrite",
    help="Overwrite existing files if they exist",
    is_flag=True,
    required=False,
)
def operating_system_mirror_command(
    context,
    operating_system,
    slug=None,
    organization_slug=None,
    directory=None,
    is_global=False,
    overwrite=False,
):
    primitive: Primitive = context.obj.get("PRIMITIVE")

    if organization_slug:
        organization = primitive.organizations.get_organization(slug=organization_slug)
    else:
        organization = primitive.organizations.get_default_organization()

    if not organization:
        if organization_slug:
            logger.error(f"No organization found with slug {organization_slug}")
            return
        else:
            logger.error("Failed to fetch default organization")
            return

    operating_system_slug = slug if slug else operating_system

    is_slug_available, _operating_system_id = (
        primitive.operating_systems._is_slug_available(
            slug=operating_system_slug,
            organization_id=organization["id"],
            is_global=is_global,
        )
    )

    if not is_slug_available and not overwrite:
        logger.info(
            f"Operating system with slug {operating_system_slug} already exists, skipping creation."
        )
        return

    try:
        iso_file_path, checksum_file_path = primitive.operating_systems.download_remote(
            operating_system, directory=directory
        )

        checksum_file_type = primitive.operating_systems.get_remote_info(
            operating_system
        )["checksum_file_type"]

        primitive.operating_systems.create(
            slug=operating_system_slug,
            iso_file=iso_file_path,
            checksum_file=checksum_file_path,
            checksum_file_type=checksum_file_type.value,
            organization_id=organization["id"],
            is_global=is_global,
            overwrite=overwrite,
        )
    except Exception as error:
        if context.obj["DEBUG"]:
            raise error
        else:
            logger.error(error)
            context.exit(1)

    logger.success("Successfully mirrored operating system")


@remotes.command("list")
@click.pass_context
def remote_operating_systems_list_command(context):
    primitive: Primitive = context.obj.get("PRIMITIVE")
    remotes_list = primitive.operating_systems.list_remotes()
    remote_slugs = [remote["slug"] for remote in remotes_list]
    newline = "\n"
    logger.info(
        f"Remote operating systems: {newline}- {f'{newline}- '.join(remote_slugs)}"
    )
