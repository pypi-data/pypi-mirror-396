import click


@click.group()
def kmer_group():
    """Kmer related analysis tools."""
    pass


def register_commands():
    from .kmer_count import count
    from .kmer_total import total

    kmer_group.add_command(count)
    kmer_group.add_command(total)


register_commands()
