import click


@click.group()
def fasta_group():
    """FASTA related tools."""
    pass


def register_commands():
    from .fasta_view import view
    from .fasta_clean import clean
    from .fasta_shuffle import shuffle
    from .fasta_info import info

    fasta_group.add_command(view)
    fasta_group.add_command(clean)
    fasta_group.add_command(shuffle)
    fasta_group.add_command(info)


register_commands()
