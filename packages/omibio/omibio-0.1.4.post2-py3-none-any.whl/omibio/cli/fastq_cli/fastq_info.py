import click
from omibio.cli.fastq_cli import fastq_group
from omibio.io import read_fastq_iter
from typing import TextIO
from omibio.sequence import Sequence

_AMBIGUOUS_BASES = {"R", "Y", "K", "M", "B", "V", "D", "H", "S", "W"}


@fastq_group.command()
@click.argument(
    "source",
    type=click.File("r"),
    required=False,
    default="-"
)
def info(source: TextIO):
    """Display information about a FASTQ file."""
    result = read_fastq_iter(source)

    seq_num = 0
    total_len = 0
    total_qual = 0

    longest = 0
    shortest = None

    total_gc = 0.0
    total_at = 0.0
    total_n = 0
    total_ambi = 0

    max_qual = 0
    min_qual = 200
    q20 = 0
    q30 = 0

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

        if entry.qual:
            for qual in entry.qual:
                score = ord(qual) - 33
                total_qual += score
                max_qual = max(max_qual, score)
                min_qual = min(min_qual, score)
                if score >= 20:
                    q20 += 1
                if score >= 30:
                    q30 += 1

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
        "\n"
        f"Average qual:\t{(total_qual / total_len):.3f}\n"
        f"Min qual:\t{min_qual}\n"
        f"Max qual:\t{max_qual}\n"
        f"q20 bases:\t{(q20 / total_len):.3f} ({q20} q20 bases)\n"
        f"q30 bases:\t{(q30 / total_len):.3f} ({q30} q30 bases)\n"
    )
