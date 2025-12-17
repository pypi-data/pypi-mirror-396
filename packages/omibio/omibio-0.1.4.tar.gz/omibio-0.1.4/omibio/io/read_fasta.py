from pathlib import Path
from typing import TYPE_CHECKING, Generator, TextIO, cast
from os import PathLike
import warnings
if TYPE_CHECKING:
    from omibio.bio import SeqCollections, SeqEntry

VALID_NT = {
    "A", "T", "U", "C", "G", "R", "Y", "K",
    "M", "B", "V", "D", "H", "S", "W", "N"
}
VALID_AA = {
    "A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M",
    "N", "P", "Q", "R", "S", "T", "V", "W", "Y", "X", "*"
}


class FastaFormatError(Exception):

    def __init__(self, message):
        super().__init__(message)


def read_fasta_iter(
    source: str | TextIO | PathLike,
    strict: bool = False,
    warn: bool = True,
    output_strict: bool = False,
    skip_invalid_seq: bool = False,
) -> Generator["SeqEntry"]:
    """Parse a FASTA file and return a Generator.

    Raises:
        FileNotFoundError:
            If the specified file is not found.
        FastaFormatError:
            If the FASTA format is invalid.
        FastaFormatError:
            If the sequence contains invalid characters.
        FastaFormatError:
            If the sequence name is missing.
        FastaFormatError:
            If the sequence is missing.

    Yields:
        SeqEntry:
            SeqEntry objects for each sequence in the FASTA file.
    """

    from omibio.sequence import Sequence, Polypeptide
    from omibio.bio import SeqEntry

    if hasattr(source, "read"):
        fh = cast(TextIO, source)
        file_name = "<stdin>"
        faa = False
    else:
        file_path = Path(source)
        if not file_path.exists():
            raise FileNotFoundError(f"File '{source}' not found.")

        suffix = file_path.suffix.lower()
        if suffix not in {".faa", ".fa", ".fasta", ".fna"}:
            raise FastaFormatError(
                f"Invalid format to read: {suffix}"
            )
        faa = (suffix == ".faa")
        file_name = str(file_path)
        fh = open(file_path, "r")

    current_name = None
    current_seq: list[str] = []
    allowed_set = VALID_AA if faa else VALID_NT

    def push_entry():
        if current_name is None:
            return
        if not current_seq:
            msg = f"Sequence missing for {current_name}"
            if strict:
                raise FastaFormatError(msg)
            elif warn:
                warnings.warn(msg + ", skip record")
            return

        seq_str = "".join(current_seq)
        current_seq.clear()
        if faa:
            seq_obj = Polypeptide(seq_str, strict=output_strict)
        else:
            seq_obj = Sequence(seq_str, strict=output_strict)

        return SeqEntry(seq=seq_obj, seq_id=current_name, source=file_name)

    try:
        for i, line in enumerate(fh, start=1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue

            if line.startswith(">"):
                entry = push_entry()
                if entry:
                    yield entry

                current_name = line[1:].strip()

                if not current_name:
                    if strict:
                        raise FastaFormatError(
                            f"Sequence name missing in line {i}"
                        )
                    elif warn:
                        warnings.warn(
                            f"Sequence name missing in line {i}, "
                            "skip record"
                        )
                    current_name = None
                    current_seq.clear()
                    continue

            else:
                if current_name is None:
                    continue
                # Store sequence.
                line = line.upper()
                skip_record = False
                if strict or warn or skip_invalid_seq:
                    if any(c not in allowed_set for c in line):
                        if strict:
                            raise FastaFormatError(
                                f"Invalid sequence in line {i}: {line}"
                            )
                        elif warn:
                            warnings.warn(
                                f"Invalid sequence in line {i}: {line}, "
                                f"{'skip' if skip_invalid_seq else 'invalid'} "
                                "record"
                            )
                        if skip_invalid_seq:
                            skip_record = True
                if skip_record:
                    current_name = None
                    current_seq.clear()
                    continue

                current_seq.append(line)

        # Store the last sequence when the file ends
        entry = push_entry()
        if entry:
            yield entry
    finally:
        if not hasattr(source, "read"):
            fh.close()


def read_fasta(
    source: str | TextIO | PathLike,
    strict: bool = False,
    output_strict: bool = False,
    warn: bool = True,
    skip_invalid_seq: bool = False
) -> "SeqCollections":
    """Parse a FASTA file and return a SeqCollections object.

    Args:
        source (str | TextIO | PathLike):
            Path to the FASTA file or a file-like object.
        strict (bool, optional):
            Whether to raise errors on invalid sequences. Defaults to False.
        output_strict (bool, optional):
            Whether to enforce strictness on the output sequences.
            Defaults to False.
        warn (bool, optional):
            Whether to issue warnings on invalid sequences. Defaults to True.
        skip_invalid_seq (bool, optional):
            Whether to skip invalid sequences. Defaults to False.

    Returns:
        SeqCollections:
            A SeqCollections object containing the parsed sequences.
    """

    from omibio.bio import SeqCollections

    entries = []
    for entry in read_fasta_iter(
        source,
        strict=strict,
        output_strict=output_strict,
        warn=warn,
        skip_invalid_seq=skip_invalid_seq
    ):
        entries.append(entry)

    if hasattr(source, "read"):
        file_name = "<stdin>"
    else:
        file_name = str(source)

    return SeqCollections(entries=entries, source=file_name)


def main():
    input_path = r"./examples/data/example_lots_of_seqs.fasta"
    for entry in read_fasta(
        input_path, strict=False, skip_invalid_seq=True, warn=True
    ):
        print(entry.source)


if __name__ == "__main__":
    main()
