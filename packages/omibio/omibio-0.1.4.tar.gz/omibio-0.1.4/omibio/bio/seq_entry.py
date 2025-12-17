from dataclasses import dataclass, field
from omibio.sequence import Sequence, Polypeptide
from omibio.utils.truncate_repr import truncate_repr
from typing import Any


@dataclass(slots=True)
class SeqEntry:
    """Class to hold a sequence entry with associated metadata,
    returned by file parsing functions.

    Raises:
        TypeError:
            If the input types are incorrect.
    """
    seq: Sequence | Polypeptide
    seq_id: str

    source: str | None = None
    qual: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.seq, (Sequence, Polypeptide)):
            raise TypeError(
                "SeqEntry argument 'seq' must be Sequence Polypeptide, got "
                + type(self.seq).__name__
            )
        if not isinstance(self.seq_id, str):
            raise TypeError(
                "SeqEntry argument 'seq_id' must be str, got "
                + type(self.seq_id).__name__
            )

    def __str__(self) -> str:
        return str(self.seq)

    def __repr__(self) -> str:
        repr_seq = truncate_repr(str(self.seq))
        text = f"SeqEntry({repr_seq}, seq_id={self.seq_id!r}"
        if self.qual is not None:
            repr_qual = truncate_repr(self.qual)
            text += f", qual={repr_qual}"
        text += ")"
        return text


def main():
    seq = Sequence("ACTG")
    seq_entry = SeqEntry(seq, seq_id="test")
    print(repr(seq_entry))
    print(seq_entry.seq)


if __name__ == "__main__":
    main()
