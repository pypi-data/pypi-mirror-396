import click
from omibio.cli.fasta_cli import fasta_group
from omibio.io import read_fasta, write_fasta
from typing import TextIO


@fasta_group.command()
@click.argument(
    "source",
    type=click.File("r"),
    required=False,
    default="-"
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path."
)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Output file path."
)
def shuffle(
    source: TextIO,
    output: str | None,
    seed: int | None
):
    """
    Shuffle the sequences in the FASTA file
    and output them to the specified file.
    """
    from omibio.sequence.seq_utils.shuffle_seq import shuffle_seq
    import random

    res = {}
    rng = random.Random(seed)

    seqs = read_fasta(source).seq_dict()

    for name, seq in seqs.items():
        seq_seed = rng.randint(0, 2**32 - 1)
        shuffled = shuffle_seq(seq, seed=seq_seed, as_str=True)
        res[name] = shuffled

    if output is not None:
        write_fasta(file_name=output, seqs=res)
    else:
        for line in write_fasta(seqs=res):
            click.echo(line)
