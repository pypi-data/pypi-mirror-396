from dataclasses import dataclass, field
from omibio.bio.analysis_result import AnalysisResult
from omibio.bio.seq_interval import SeqInterval
from typing import Iterator


@dataclass
class IntervalResult(AnalysisResult):
    """Store data returned by analytical functions for interval types,
    is a subclass of AnalysisResult.

    Args:
        AnalysisResult:
            Base class for analysis results.

    Raises:
        TypeError:
            If the input types are incorrect.
    """

    intervals: list[SeqInterval] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.intervals, list):
            raise TypeError(
                "IntervalResult argument 'intervals' must be list, got "
                + type(self.intervals).__name__
            )

    def __len__(self) -> int:
        return len(self.intervals)

    def __iter__(self) -> Iterator[SeqInterval]:
        return iter(self.intervals)

    def __getitem__(self, idx: int | slice) -> SeqInterval | list[SeqInterval]:
        return self.intervals[idx]

    def __repr__(self) -> str:
        return (
            f"IntervalResult(intervals={self.intervals!r}, "
            f"seq_id={self.seq_id!r}, type={self.type!r})"
        )

    def __str__(self) -> str:
        return str(self.intervals)


def main():
    from omibio.viz import plot_motifs
    intervals = [
        SeqInterval(0, 4, nt_seq="ACTG"), SeqInterval(8, 12, nt_seq="ACTG")
    ]
    result = IntervalResult(
        intervals=intervals, seq_id="test", type="motif", plot_func=plot_motifs
    )
    print(result)
    print(type(result))


if __name__ == "__main__":
    main()
