import click
from omibio.cli import cli
from omibio.sequence.seq_utils.random_seq import random_fasta as rf


@cli.command()
@click.argument("output", type=str, required=False)
@click.option(
    "-n", "--number",
    type=int,
    default=1,
    help="Number of random sequences to generate (default: 1)."
)
@click.option(
    "-p", "--prefix",
    type=str,
    default="random_seq",
    help="Prefix for sequence IDs (default: 'random_seq')."
)
@click.option(
    "-l", "--length",
    type=int,
    default=100,
    help="Length of sequences"
)
@click.option(
    "--alphabet", "-a",
    type=str,
    default="ATGC",
    help="Alphabet to sample from (default: ATGC)."
)
@click.option(
    "--seed",
    type=int,
    help="Random seed for reproducibility."
)
def random_fasta(
    output: str,
    length: int,
    number: int,
    prefix: str,
    alphabet: str,
    seed: int | None
) -> None:
    """Generate random nucleotide sequence(s) and output in FASTA format."""

    res = rf(
        file_path=output, seq_num=number, length=length,  alphabet=alphabet,
        prefix=prefix, seed=seed
    )
    if output is not None:
        click.echo(f"Success: file writed to {output}")
    else:
        for line in res:
            click.echo(line)
