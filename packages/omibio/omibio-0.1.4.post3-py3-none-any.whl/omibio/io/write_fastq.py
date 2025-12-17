from pathlib import Path
from omibio.bio import SeqCollections


def write_fastq(
    seqs:  SeqCollections,
    file_name: str | None = None,
) -> list[str]:
    """Write sequences to a FASTQ file or return as list of strings.

    Args:
        seqs (SeqCollections):
            A SeqCollections object containing SeqEntry objects.
        file_name (str | None, optional):
            Path to the output FASTQ file. If None, the function
            returns the FASTQ lines as a list of strings.
            Defaults to None.

    Raises:
        TypeError:
            If the input types are incorrect.
        OSError:
            If there is an error writing to the file.

    Returns:
        list[str]:
            List of strings representing the FASTQ file lines.
    """

    if not seqs:
        return []
    if not isinstance(seqs, SeqCollections):
        raise TypeError(
            "write_fastq() argument 'seqs' must be SeqCollections, "
            f"got {type(seqs).__name__}"
        )

    lines = []

    for entry in seqs.entry_list():
        lines.append(f"@{entry.seq_id}")
        lines.append(str(entry.seq))
        lines.append("+")
        lines.append(str(entry.qual))

    if file_name is not None:
        try:
            file_path = Path(file_name)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open("w", encoding="utf-8") as f:
                f.writelines(line + "\n" for line in lines)
        except OSError as e:
            raise OSError(
                f"Could not write fastq to '{file_name}': {e}"
            ) from e

    return lines


def main():
    from omibio.io.read_fastq import read_fastq

    input_path = r"./examples/data/example_fastq.fastq"
    output_path = r"./examples/output/write_fastq_output.fastq"

    seqs = read_fastq(input_path)
    lines = write_fastq(seqs, output_path)
    print(output_path)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
