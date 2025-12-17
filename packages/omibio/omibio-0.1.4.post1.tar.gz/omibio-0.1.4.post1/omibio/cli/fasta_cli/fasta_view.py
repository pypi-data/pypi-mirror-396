import click
from omibio.cli.fasta_cli import fasta_group
from omibio.io import read_fasta_iter
from typing import TextIO


@fasta_group.command()
@click.argument(
    "source",
    type=click.File("r"),
    required=False,
    default="-"
)
@click.option(
    "--head", "-h",
    type=int,
)
@click.option(
    "--tail", "-t",
    type=int,
)
@click.option(
    "--lengths", "-l",
    is_flag=True
)
@click.option(
    "--id-only", "-id",
    is_flag=True
)
@click.option(
    "--verbose", "-v",
    is_flag=True
)
@click.option(
    "--min-length", "-min",
    type=int,
)
@click.option(
    "--max-length", "-max",
    type=int,
)
def view(
    source: TextIO,
    head: int,
    tail: int,
    id_only: bool,
    lengths: bool,
    verbose: bool,
    min_length: int,
    max_length: int
):
    """View FASTA file."""

    count = 0
    result = read_fasta_iter(source)

    if min_length and max_length:
        if min_length > max_length:
            raise ValueError(
                "fasta view argument 'min_length' cannot be"
                "larger than 'max_length'"
            )

    def message(entry) -> str:
        nonlocal count
        count += 1
        if id_only:
            return entry.seq_id
        elif lengths:
            return (f"{entry.seq_id}\t{len(entry.seq)}")
        return f">{entry.seq_id}\n{entry.seq}"

    if min_length or max_length:
        def check_length(entry) -> bool:
            length = len(entry.seq)
            return not (
                (min_length and length < min_length)
                or (max_length and length > max_length)
            )
    else:
        def check_length(entry) -> bool:
            return True

    if verbose:
        click.echo(f"File: {source.name}")

    if head is not None:
        for entry in result:
            if check_length(entry):
                click.echo(message(entry))
            if count >= head:
                break

    if tail is not None:
        from collections import deque
        entries: deque = deque(maxlen=tail)
        for entry in result:
            if check_length(entry):
                entries.append(entry)
        for entry in entries:
            click.echo(message(entry))

    if not head and not tail:
        for entry in result:
            if check_length(entry):
                click.echo(message(entry))

    if verbose:
        click.echo(f"All {count} sequence(s) showed")
