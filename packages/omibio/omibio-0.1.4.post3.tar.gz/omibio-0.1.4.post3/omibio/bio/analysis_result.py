from dataclasses import dataclass, field
from matplotlib.axes import Axes
from typing import Callable, Any
from abc import ABC


@dataclass
class AnalysisResult(ABC):
    """An abstract base class used to store the results of analysis functions,
    including basic information such as sequence ID, and methods for plotting.

    Args:
        ABC:
            Abstract Base Class.

    Raises:
        TypeError:
            If the input types are incorrect.
        NotImplementedError:
            If the plot method is called but no plotting function is defined.
    """

    type: str | None = None
    seq_id: str | None = None
    plot_func: Callable | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.type is not None and not isinstance(self.type, str):
            raise TypeError(
                "AnalysisResult argument 'type' must be str, got "
                + type(self.type).__name__
            )
        if self.seq_id is not None and not isinstance(self.seq_id, str):
            raise TypeError(
                "AnalysisResult argument 'seq_id' must be str, got "
                + type(self.seq_id).__name__
            )
        if self.plot_func is not None and not callable(self.plot_func):
            raise TypeError(
                "AnalysisResult argument 'plot_func' must be Callable, got "
                + type(self.plot_func).__name__
            )
        if not isinstance(self.metadata, dict):
            raise TypeError(
                "AnalysisResult argument 'metadata' must be dict, got "
                + type(self.plot_func).__name__
            )

    def plot(self, **kwargs) -> Axes:
        """Plot the analysis result using the associated plotting function."""
        if self.plot_func is None:
            raise NotImplementedError(
                "Plotting is not supported for this analysis result."
            )

        return self.plot_func(self, **kwargs)


def main():
    ...


if __name__ == "__main__":
    main()
