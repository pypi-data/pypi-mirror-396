from importlib.metadata import version
from omibio.sequence import Sequence, Polypeptide
from omibio.bio import (
    SeqInterval,
    SeqCollections,
    SeqEntry,
    AnalysisResult,
    IntervalResult,
    KmerResult
)
from omibio.sequence.seq_utils.clean import CleanReport, CleanReportItem
from omibio.io.read_fasta import FastaFormatError
from omibio.io.read_fastq import FastqFormatError

__version__ = version("omibio")

__all__ = [
    "Sequence", "Polypeptide",
    "SeqInterval", "SeqCollections", "SeqEntry",
    "AnalysisResult", "IntervalResult", "KmerResult",
    "CleanReport", "CleanReportItem",
    "FastaFormatError",
    "FastqFormatError"
]
