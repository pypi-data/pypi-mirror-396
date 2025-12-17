import click


@click.version_option(
    version="0.1.3",
    prog_name="omibio",
    message="%(prog)s %(version)s"
)
@click.group()
def cli():
    """A lightweight and easy-to-use python bioinformatics toolkit."""
    pass


def register_commands():
    from omibio.cli.fasta_cli import fasta_group
    from omibio.cli.fastq_cli import fastq_group
    from omibio.cli.gc_cli import gc_group
    from omibio.cli.orf_cli import orf_group
    from omibio.cli.random_fasta_cli import random_fasta
    from omibio.cli.kmer_cli import kmer_group
    from omibio.cli.plot_cli import plot_group

    cli.add_command(gc_group, name="gc")
    cli.add_command(fasta_group, name="fasta")
    cli.add_command(fastq_group, name="fastq")
    cli.add_command(orf_group, name="orf")
    cli.add_command(kmer_group, name="kmer")
    cli.add_command(plot_group, name="plot")
    cli.add_command(random_fasta)


register_commands()
