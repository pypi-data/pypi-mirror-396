import click
from omibio.io import read_fasta
from omibio.cli.gc_cli import gc_group
from omibio.analysis import sliding_gc
from omibio.sequence import Polypeptide
import csv


@gc_group.command()
@click.argument(
    "source",
    type=click.File("r"),
    required=False,
    default="-"
)
@click.option(
    "--window",
    type=int,
    default=100,
    help="window size. Defaults to 100."
)
@click.option(
    "--step",
    type=int,
    default=10,
    help="step size. Defaults to 10."
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Write details to a file in csv format"
)
@click.option(
    "--summary", "-s",
    is_flag=True
)
def window_gc(
    source: str,
    window: int,
    step: int,
    output: str | None,
    summary: bool
):
    """
    Calculate and plot sliding window GC content for sequences in a FASTA file.
    """

    entries = read_fasta(source)

    if summary:
        for entry in entries:
            gc_vals = []
            seq = entry.seq
            if isinstance(seq, Polypeptide):
                raise TypeError(
                    "GC content can only be calculated for nucleotide "
                    "sequences, got Polypeptide"
                )
            result = sliding_gc(
                seq, window=window, step=step, seq_id=entry.seq_id
            )

            for interval in result:
                if (gc_val := interval.gc) is not None:
                    gc_vals.append(gc_val)

            average = sum(gc_vals) / len(gc_vals)
            click.echo(
                f"{entry.seq_id}\tmean={average:.2f}%\t"
                f"max={max(gc_vals)}%\tmin={min(gc_vals)}%"
            )
    else:
        rows = [["seq_id", "start", "end", "gc"]]
        for entry in entries:
            seq = entry.seq
            if isinstance(seq, Polypeptide):
                raise TypeError(
                    "GC content can only be calculated for nucleotide "
                    "sequences, got Polypeptide"
                )
            for itv in list(sliding_gc(
                seq, window=window, step=step, seq_id=entry.seq_id
            )):
                rows.append([
                    str(itv.seq_id), str(itv.start), str(itv.end), str(itv.gc)
                ])
        if output is not None:
            with open(output, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter="\t")
                writer.writerows(rows)
                click.echo(f"Written to {output}")
        else:
            for row in rows:
                click.echo("\t".join(row))
