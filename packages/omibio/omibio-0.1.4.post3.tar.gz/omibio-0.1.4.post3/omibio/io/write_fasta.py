from pathlib import Path
from omibio.sequence import Sequence, Polypeptide
from omibio.bio import SeqCollections
from typing import Mapping


def write_fasta(
    seqs: Mapping[str, Sequence | Polypeptide | str] | SeqCollections,
    file_name: str | None = None,
    line_len: int = 60
) -> list[str]:
    """Write sequences to a FASTA file or return as list of strings.

    Args:
        seqs (Mapping[str, Sequence  |  Polypeptide  |  str] | SeqCollections):
            A mapping of sequence names to Sequence or Polypeptide objects,
            or a SeqCollections object.
        file_name (str | None, optional):
            Path to the output FASTA file. If None, the function
            returns the FASTA lines as a list of strings.
            Defaults to None.
        line_len (int, optional):
            Maximum line length for sequences in the FASTA output.
            Defaults to 60.

    Raises:
        TypeError:
            If the input types are incorrect.
        OSError:
            If there is an error writing to the file.

    Returns:
        list[str]:
            List of strings representing the FASTA file lines.
    """

    if not seqs:
        return []

    if isinstance(seqs, SeqCollections):
        seq_dict = seqs.seq_dict()
    elif isinstance(seqs, dict):
        seq_dict = seqs
    else:
        raise TypeError(
            "write_fasta() argument 'seqs' must be dict or SeqCollections, "
            f"got {type(seqs).__name__}"
        )

    lines = []

    for name, seq in seq_dict.items():
        if not isinstance(name, str):
            raise TypeError(
                "write_fasta() Sequence name must be str, got "
                + type(name).__name__
            )

        seq_str = str(seq).replace("\n", "")
        lines.append(f">{name}")

        for i in range(0, len(seq_str), line_len):
            lines.append(seq_str[i:i+line_len])

    if file_name is not None:
        try:
            file_path = Path(file_name)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_name, "w", encoding="utf-8") as f:
                f.writelines(line + "\n" for line in lines)

        except OSError as e:
            raise OSError(
                f"Could not write fasta to '{file_name}': {e}"
            ) from e

    return lines


def main():
    from omibio.io.read_fasta import read_fasta

    input_path = r"./examples/data/example_short_seqs.fasta"
    output_path = r"./examples/output/write_fasta_output.fasta"

    seqs = read_fasta(input_path)
    write_fasta(file_name=output_path, seqs=seqs)
    print(output_path)


if __name__ == "__main__":
    main()
