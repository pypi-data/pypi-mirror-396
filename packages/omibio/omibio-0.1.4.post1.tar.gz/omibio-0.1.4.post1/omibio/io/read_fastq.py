from pathlib import Path
from typing import TYPE_CHECKING, Iterator, TextIO, cast
from os import PathLike
import warnings
if TYPE_CHECKING:
    from omibio.bio import SeqCollections, SeqEntry

VALID_NT = set("ATUCGRYKMBVDHSWN")


class FastqFormatError(Exception):

    def __init__(self, message):
        super().__init__(message)


def read_fastq_iter(
    source: str | TextIO | PathLike,
    strict: bool = False,
    warn: bool = True,
    skip_invalid_seq: bool = False
) -> Iterator["SeqEntry"]:
    """Parse a FASTA file and return a Generator.

    Raises:
        FileNotFoundError:
            If the specified file is not found.
        FastqFormatError:
            If the FASTQ format is invalid.
        FastqFormatError:
        If the sequence contains invalid characters.
        FastqFormatError:
            If the sequence name is missing.
        FastqFormatError:
            If the sequence is missing.
        FastqFormatError:
            If the quality scores length does not match the sequence length.
        FastqFormatError:
            If the '+' line is invalid.

    Yields:
        SeqEntry:
            SeqEntry objects for each sequence in the FASTQ file.
    """

    from omibio.bio import SeqEntry
    from omibio.sequence import Sequence

    if hasattr(source, "read"):
        fh = cast(TextIO, source)
        file_name = "<stdin>"
    else:
        file_path = Path(source)
        if not file_path.exists():
            raise FileNotFoundError(f"File '{source}' not found.")

        suffix = file_path.suffix.lower()
        if suffix not in {".fastq", ".fq"}:
            raise FastqFormatError(
                f"Invalid format to read: {suffix}"
            )
        file_name = str(file_path)
        fh = open(file_path, "r")

    try:
        line_num = 0

        while True:
            header = fh.readline()
            line_num += 1
            if not header:
                break

            header = header.rstrip()
            if not header:
                continue

            if not header.startswith("@"):
                raise FastqFormatError(
                    f"Line {line_num}: FASTQ header must start with '@', "
                    f"got: {header}"
                )
            seq = fh.readline()
            plus = fh.readline()
            qual = fh.readline()
            line_num += 3

            seq, plus, qual = seq.rstrip(), plus.rstrip(), qual.rstrip()

            if (not seq) or (not plus) or (not qual):
                raise FastqFormatError(
                    f"File ends prematurely at line {line_num}"
                )

            if not plus.startswith("+"):
                if strict:
                    raise FastqFormatError(
                        f"Line {line_num}: invalid '+' line: {plus}"
                    )
                elif warn:
                    warnings.warn(
                        f"Line {line_num}: invalid '+' line: {plus}, "
                        "skip record"
                    )
                continue

            if len(seq) != len(qual):
                if strict:
                    raise FastqFormatError(
                        f"Line {line_num-2} & {line_num}: Sequence / quality "
                        f"length mismatch: ({len(seq)} vs {len(qual)})"
                    )
                elif warn:
                    warnings.warn(
                        f"Line {line_num-2} & {line_num}: Sequence / quality, "
                        f"length mismatch: ({len(seq)} vs {len(qual)})"
                        "skip record"
                    )
                continue

            skip_record = False
            for char in seq.upper():
                if char not in VALID_NT:
                    if strict:
                        raise FastqFormatError(
                            f"Invalid Sequence in line {line_num-2}: {seq}"
                        )
                    elif warn:
                        warnings.warn(
                            f"Invalid Sequence in line {line_num-2}: {seq}, "
                            f"{"skip" if skip_invalid_seq else "invalid"} "
                            "record"
                        )
                    if skip_invalid_seq:
                        skip_record = True
                    break
            if skip_record:
                continue

            yield SeqEntry(
                    seq=Sequence(seq), seq_id=header[1:],
                    qual=qual, source=file_name
                )
    finally:
        if not hasattr(source, "read"):
            fh.close()


def read_fastq(
    source: str | TextIO | PathLike,
    strict: bool = False,
    warn: bool = True,
    skip_invalid_seq: bool = False
) -> "SeqCollections":
    """Parse a FASTQ file and return a SeqCollections object.

    Args:
        source (str | TextIO | PathLike):
            Path to the FASTQ file or a file-like object.
        strict (bool, optional):
            Whether to raise errors on format issues. Defaults to False.
        warn (bool, optional):
            Whether to issue warnings on format issues. Defaults to True.
        skip_invalid_seq (bool, optional):
            Whether to skip records with invalid sequences. Defaults to False.

    Returns:
        SeqCollections:
            A SeqCollections object containing the parsed sequences.
    """

    from omibio.bio import SeqCollections

    entries = []
    for entry in read_fastq_iter(
        source,
        strict=strict,
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
    input_path = r"./examples/data/example_fastq.fastq"
    result = read_fastq_iter(input_path, warn=True)
    for entry in result:
        print(entry.qual)


if __name__ == "__main__":
    main()
