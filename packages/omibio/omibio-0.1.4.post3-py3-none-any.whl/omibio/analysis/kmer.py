from omibio.sequence.sequence import Sequence, Polypeptide
from omibio.bio import KmerResult
from collections import Counter
from omibio.sequence.seq_utils.complement import reverse_complement
from omibio.viz import plot_kmer


def kmer(
    seq: Sequence | str | Polypeptide,
    k: int,
    seq_id: str | None = None,
    canonical: bool = False,
    min_count: int = 1,
) -> KmerResult:
    """Count k-mers in a given sequence.

    Args:
        seq (Sequence | str | Polypeptide):
            Input sequence to analyze.
        k (int):
            Length of the k-mers to count.
        seq_id (str | None, optional):
            An optional identifier for the sequence. Defaults to None.
        canonical (bool, optional):
            Whether to count canonical k-mers (considering reverse
            complements). Defaults to False.
        min_count (int, optional):
            Minimum count threshold for k-mers to include in the result.
            Defaults to 1.

    Raises:
        TypeError:
            If the input sequence is not of type Sequence, Polypeptide,
            or string.
        TypeError:
            If k is not of type int.
        TypeError:
            If min_count is not of type int.
        ValueError:
            If k is not a positive integer.
        ValueError:
            If min_count is negative.

    Returns:
        KmerResult:
            An object containing k-mer counts and metadata.
    """

    if canonical:
        cache: dict[str, str] = {}

        def get_canonical(kmer_seq):
            if kmer_seq in cache:
                return cache[kmer_seq]
            rc = reverse_complement(kmer_seq, as_str=True)
            canon = min(kmer_seq, rc)
            cache[kmer_seq] = cache[rc] = canon
            return canon
    else:
        def get_canonical(kmer_seq):
            return kmer_seq

    if not isinstance(seq, (Sequence, str)):
        raise TypeError(
            "kmer() argument 'seq' must be Sequence or str, got "
            + type(seq).__name__
        )
    if not isinstance(k, int):
        raise TypeError(
            f"kmer() argument 'k' must be int, got {type(k).__name__}"
        )
    if not isinstance(min_count, int):
        raise TypeError(
            "kmer() argument 'min_count' must be int, got "
            + type(min_count).__name__
        )
    if k <= 0:
        raise ValueError(
            f"kmer() argument 'k' must be a positive number, got {k}"
        )
    if min_count < 0:
        raise ValueError(
            "kmer() argument 'min_count' must be a non-negative number, got "
            + str(min_count)
        )

    seq_str = str(seq).upper()
    n = len(seq_str)

    if k > n:
        return KmerResult(
            k=k, counts=dict(), seq_id=seq_id, type="kmer", plot_func=plot_kmer
        )

    kmer_counter: dict = Counter()

    for i in range(n - k + 1):
        curr_kmer = seq_str[i: i+k]
        kmer_counter[get_canonical(curr_kmer)] += 1

    if min_count > 1:
        kmer_counter = Counter(
            {kmer: c for kmer, c in kmer_counter.items() if c >= min_count}
        )
    return KmerResult(
        k=k, counts=kmer_counter, seq_id=seq_id,
        type="kmer", plot_func=plot_kmer
    )


def main():
    from omibio.io import read_fasta
    seq = read_fasta(
        r"./examples/data/example_single_long_seq.fasta"
    )["example"]
    res = kmer(seq, 3, min_count=30, seq_id="test")
    print(res)
    print(repr(res))
    print(res["ACT"])
    res.plot(show=True)


if __name__ == "__main__":
    main()
