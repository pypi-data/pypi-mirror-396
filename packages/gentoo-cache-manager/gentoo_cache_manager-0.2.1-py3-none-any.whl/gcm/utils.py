import click
import portage
from portage.dbapi.dep_expand import dep_expand
from portage.exception import PackageNotFound


def warn(message: str) -> None:
    click.echo(click.style(message, 'yellow'))


def pretty_name(name: str) -> str:
    return click.style(name, 'green', bold=True)


def normalize_package_name(name: str) -> str:
    dbapi = portage.db[portage.root]['porttree'].dbapi
    package: str = dep_expand(name, mydb=dbapi, settings=dbapi.settings).cp
    if package.startswith('null/') or (
        '/' in name and not dbapi.cp_list(package)
    ):
        raise PackageNotFound(name)

    return package
