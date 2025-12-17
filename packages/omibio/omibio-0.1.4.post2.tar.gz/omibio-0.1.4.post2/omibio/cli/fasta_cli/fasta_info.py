import click
from omibio.cli.fasta_cli import fasta_group
from omibio.io import read_fasta_iter
from typing import TextIO
from omibio.sequence import Sequence

_AMBIGUOUS_BASES = {"R", "Y", "K", "M", "B", "V", "D", "H", "S", "W"}


@fasta_group.command()
@click.argument(
    "source",
    type=click.File("r"),
    required=False,
    default="-"
)
def info(source: TextIO):
    """Display information about a FASTA file."""
    result = read_fasta_iter(source)

    seq_num = 0
    total_len = 0
    longest = 0
    shortest = None

    total_gc = 0.0
    total_at = 0.0
    total_n = 0
    total_ambi = 0

    for entry in result:
        seq = entry.seq
        length = len(seq)

        seq_num += 1
        total_len += length
        longest = max(longest, length)

        if not shortest:
            shortest = length
        else:
            shortest = min(shortest, length)

        if isinstance(seq, Sequence):
            total_gc += float(seq.gc_content())
            total_at += float(seq.at_content())
        total_n += seq.count("N")
        for base in _AMBIGUOUS_BASES:
            total_ambi += seq.count(base)

    click.echo(
        f"Sequences:\t{seq_num}\n"
        f"Total length:\t{total_len} bp\n"
        f"Longest:\t{longest} bp\n"
        f"Shortest:\t{shortest} bp\n"
        f"Average length:\t{total_len // seq_num} bp\n"
        "\n"
        f"GC content:\t{(total_gc / seq_num):.3f}\n"
        f"AT content:\t{(total_at / seq_num):.3f}\n"
        f"N content:\t{(total_n / total_len):.3f} ({total_n} Ns)\n"
        f"Ambiguous:\t{(total_ambi / total_len):.3f} ({total_ambi} Ambiguous)\n"  # noqa
    )
