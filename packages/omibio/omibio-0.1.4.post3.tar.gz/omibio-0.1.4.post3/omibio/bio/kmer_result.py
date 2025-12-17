from dataclasses import dataclass, field
from omibio.bio.analysis_result import AnalysisResult
from typing import Iterator, Iterable


@dataclass
class KmerResult(AnalysisResult):
    """lass to hold kmer counting results. is a subclass of AnalysisResult.

    Args:
        AnalysisResult:
            Base class for analysis results.

    Raises:
        TypeError:
            If the input types are incorrect.
    """

    k: int = field(default_factory=int)
    counts: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.counts, dict):
            raise TypeError(
                "KmerResult argument 'counts' must be dict, got "
                + type(self.counts).__name__
            )

    def items(self) -> Iterable[tuple[str, int]]:
        """Return an iterator over the (kmer, count) pairs."""
        return self.counts.items()

    def keys(self) -> Iterable[str]:
        """Return an iterator over the kmers."""
        return self.counts.keys()

    def values(self) -> Iterable[int]:
        """Return an iterator over the counts."""
        return self.counts.values()

    def __len__(self) -> int:
        return len(self.counts)

    def __iter__(self) -> Iterator[str]:
        return iter(self.counts)

    def __getitem__(self, key: str) -> int:
        return self.counts[key]

    def __repr__(self) -> str:
        return (
            f"KmerResult(counts={self.counts!r}, "
            f"seq_id={self.seq_id!r}, type={self.type!r})"
        )

    def __str__(self) -> str:
        return str(self.counts)


def main():
    ...


if __name__ == "__main__":
    main()
