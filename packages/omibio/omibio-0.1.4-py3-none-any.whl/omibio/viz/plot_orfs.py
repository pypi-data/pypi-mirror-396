import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.axes import Axes
from omibio.bio import SeqInterval
from omibio.bio import IntervalResult


def plot_orfs(
    orfs: list[SeqInterval] | IntervalResult,
    seq_length: int | None = None,
    ax: Axes | None = None,
    show: bool = False
) -> Axes:
    """Plot Open Reading Frames (ORFs) along a sequence.

    Args:
        orfs (list[SeqInterval] | IntervalResult):
            List of ORF intervals or an IntervalResult object.
        seq_length (int | None, optional):
            Length of the sequence. Required if 'orfs' is a list.
            Defaults to None.
        ax (Axes | None, optional):
            Matplotlib Axes to plot on. If None, a new figure and axes
            will be created. Defaults to None.
        show (bool, optional):
            Whether to display the plot immediately. Defaults to False.

    Raises:
        TypeError:
            If 'orfs' is a list and 'seq_length' is not provided.

    Returns:
        Axes:
            The Matplotlib Axes object containing the plot.
    """

    if ax is None:
        _, ax = plt.subplots(figsize=(9, 3))

    if seq_length is None:
        if isinstance(orfs, IntervalResult):
            seq_length = orfs.metadata["seq_length"]
        else:
            raise TypeError(
                "plot_orfs() argument: 'seq_length' must be provided if"
                "'orfs' is a list"
            )

    frame_y = {
        '+1': 5, '+2': 4, '+3': 3,
        '-1': 2, '-2': 1, '-3': 0
    }
    bar_height = 0.4
    positive_color = "#4D84DC"
    negative_color = "#E14040"

    for i in frame_y.values():
        ax.axhline(y=i, color="#C8C7CE", linestyle="--")

    for orf in orfs:
        frame_key = f"+{orf.frame}" if orf.frame > 0 else str(orf.frame)
        y = frame_y[frame_key]
        color = positive_color if orf.strand == '+' else negative_color

        ax.broken_barh(
            [(orf.start, orf.length)],
            (y - bar_height/2, bar_height),
            facecolors=color, zorder=3
        )

    ax.set_ylim(-1, 7)
    ax.set_xlim(0, seq_length)
    ax.set_yticks(list(frame_y.values()))
    ax.set_yticklabels(list(frame_y.keys()))
    ax.set_xlabel("Sequence Position")
    ax.set_ylabel("Reading Frame")
    ax.set_title("ORF Distribution")

    legend_elements = [
        Patch(facecolor=positive_color, label="Positive strand (+)"),
        Patch(facecolor=negative_color, label="Negative strand (-)")
    ]
    ax.legend(handles=legend_elements, loc="upper right")
    ax.grid(True, linestyle='--', alpha=0.5)

    if show:
        plt.show()
    return ax


def main():
    from omibio.analysis.find_orfs import find_orfs
    from omibio.io.read_fasta import read_fasta
    seq = read_fasta(
        "./examples/data/example_single_long_seq.fasta"
    )["example"]
    orfs = find_orfs(seq, min_length=100)
    plot_orfs(orfs)
    plt.show()


if __name__ == "__main__":
    main()
