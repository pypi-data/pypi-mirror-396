from omibio.bio.seq_entry import SeqEntry
from omibio.sequence import Sequence, Polypeptide
from typing import Iterable, ItemsView, Iterator


class SeqCollections:
    """Class to hold a collection of SeqEntry objects."""

    def __init__(
        self,
        entries: Iterable[SeqEntry] | None = None,
        source: str | None = None
    ):
        """Initialization for SeqCollection.

        Args:
            entries (Iterable[SeqEntry] | None, optional):
                Iterable of SeqEntry objects to initialize the collection.
                Defaults to None.
            source (str | None, optional):
                Source information for the collection. Defaults to None.

        Raises:
            TypeError:
                If the input types are incorrect.
        """
        self._entries: dict[str, SeqEntry] = {}
        self._source = source
        if entries is not None and not isinstance(entries, Iterable):
            raise TypeError(
                "SeqCollections argument 'entries' must be Iterable "
                f"contains SeqEntry, got {type(entries).__name__}"
            )
        if entries:
            for entry in entries:
                self.add_entry(entry)

    @property
    def entries(self):
        """Return the dictionary of SeqEntry objects."""
        return self._entries

    @property
    def source(self):
        """Return the source information."""
        return self._source

    def add_entry(self, entry: SeqEntry):
        """Add a SeqEntry to the collection."""
        if not isinstance(entry, SeqEntry):
            raise TypeError(
                "SeqCollections argument 'entries' must be Iterable "
                f"contains SeqEntry, got {type(entry).__name__}"
            )
        seq_id = entry.seq_id
        if seq_id in self._entries:
            raise ValueError(
                f"Duplicate seq_id '{seq_id}'"
            )
        self._entries[seq_id] = entry

    def get_entry(self, seq_id: str) -> SeqEntry:
        """Return the SeqEntry for the given seq_id."""
        return self._entries[seq_id]

    def get_seq(self, seq_id: str) -> Sequence | Polypeptide:
        """Return the Sequence or Polypeptide for the given seq_id."""
        return self[seq_id]

    def seq_ids(self) -> list[str]:
        """Return a list of sequence IDs in the collection."""
        return list(self._entries.keys())

    def seqs(self) -> list[Sequence | Polypeptide]:
        """Return a list of sequences in the collection."""
        return [e.seq for e in self._entries.values()]

    def entry_list(self) -> list[SeqEntry]:
        """Return a list of SeqEntry objects in the collection."""
        return list(self._entries.values())

    def seq_dict(self) -> dict[str, Sequence | Polypeptide]:
        """Return a dictionary of seq_id to Sequence or Polypeptide."""
        return {e.seq_id: e.seq for e in self._entries.values()}

    def items(self) -> ItemsView[str, SeqEntry]:
        """Return an items view of the collection."""
        return self._entries.items()

    def __iter__(self) -> Iterator[SeqEntry]:
        return iter(self._entries.values())

    def __getitem__(self, seq_id: str) -> Sequence | Polypeptide:
        return self._entries[seq_id].seq

    def __contains__(self, seq_id: str) -> bool:
        return seq_id in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"SeqCollections({list(self._entries.values())!r})"

    def __str__(self) -> str:
        return str(list(self._entries.values()))


def main():
    seqs = SeqCollections(
        [
            SeqEntry(Sequence("ACTG"), seq_id="1"),
            SeqEntry(Sequence("ACTG"), seq_id="2"),
            SeqEntry(Sequence("ACTG"), seq_id="3"),
            SeqEntry(Sequence("ACTG"), seq_id="4"),
            SeqEntry(Sequence("ACTG"), seq_id="5"),
        ]
    )
    print(seqs.items())


if __name__ == "__main__":
    main()
