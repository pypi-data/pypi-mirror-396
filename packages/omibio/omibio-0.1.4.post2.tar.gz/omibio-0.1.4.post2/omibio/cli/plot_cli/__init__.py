import click


@click.group()
def plot_group():
    """Plotting related tools."""
    pass


def register_commands():
    from .plot_window_gc_cli import window_gc
    from .plot_kmer_cli import kmer

    plot_group.add_command(window_gc)
    plot_group.add_command(kmer)


register_commands()
