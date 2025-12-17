import click


@click.group()
def orf_group():
    """ORF related analysis tools."""
    pass


def register_commands():
    from .orf_find import find

    orf_group.add_command(find)


register_commands()
