# omiBio
## - A Lightweight Bioinformatics Toolkit
[![Latest Version](https://img.shields.io/github/v/release/LK923/omiBioKit?color=blue)](https://github.com/LK923/omiBioKit/releases)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![flake8](https://img.shields.io/badge/code%20style-PEP%208-blue.svg)](https://peps.python.org/pep-0008/)


<p align="center">
  <img src="https://raw.githubusercontent.com/LK923/omiBioKit/main/examples/assets/logo.png" alt="Logo" width="500"/>
</p>

## Introduction
**omiBio** is a lightweight, user-friendly Python toolkit for bioinformatics — ideal for education, research, and rapid prototyping.

 **Key features**:
-  **Robust data structures**: `Sequence`, `Polypeptide`, etc., with optional validation.
-  **Simple I/O**: Read/write bioinformatics files (e.g., FASTA) with one-liners.
-  **Analysis tools**: GC content, ORF detection, consensus sequences, sliding windows, and more.
-  **CLI included**: Run common tasks from the terminal .
-  **Basic visualization**: Built-in plotting (via matplotlib & seaborn) for quick insights.
-  **Functional & OOP APIs**: Use classes or convenient wrapper functions.

## Modules Overview

The **omiBio** toolkit is organized into the following modules:

| Module | Purpose | Key Classes / Functions |
|--------|---------|------------------------|
| `omibio.sequence` | Sequence-type data structures | `Sequence`, `Polypeptide` |
| `omibio.bio` | Biological objects and data containers | `SeqInterval`, `AnalysisResult` |
| `omibio.io` | File I/O for common bioinformatics formats | `read_fasta()`, `read_fastq()` |
| `omibio.analysis` | Sequence analysis functions | `gc()`, `sliding_gc()`, `find_orfs()` |
| `omibio.utils` | General-purpose utility functions | `truncate_repr()` |
| `omibio.viz` | Simple and easy-to-use data visualization | `plot_orf()`, `plot_sliding_gc()` |
| `omibio.cli` | Command-line interfaces for common workflows | `omibio random-fasta`, `omibio clean` |

## Release Notes - omiBio [v0.1.4] 12/14/25

### Performance & Core I/O
- **Optimized FASTA parsing**  
  Introduced the generator-based `read_fasta_iter()` to improve performance, refine error handling, and add a configurable warning system.  
  The existing `read_fasta()` API remains unchanged for external use and continues to return `SeqCollections`, allowing users to choose between eager and lazy parsing.  
  Both `read_fasta()` and `read_fasta_iter()` now accept `TextIO` and `PathLike` objects as data sources.

- **FASTQ support**  
  Added `read_fastq()` and `write_fastq()` with the same design philosophy as the FASTA APIs.  
  A generator interface, `read_fastq_iter()`, is also provided.  
  All FASTQ I/O functions support `TextIO` and `PathLike` inputs.

- **Flexible file writing**  
  All sequence writing functions can now return a list of formatted strings when no output file is specified.

### CLI Improvements
- Refactored and streamlined the CLI structure.
- Improved existing commands and added new ones, including:
  - `omibio fasta view`
  - `omibio fastq to-fasta`
  - `omibio kmer count`
- All CLI commands support `stdin`/`stdout` and can be composed in Unix-style pipelines.

### API & Data Model Changes
- Removed the `Gene` and `Genome` classes, which overlapped in functionality with `SeqEntry` and `SeqCollections`.
- Made the `Sequence` and `Polypeptide` classes immutable.
- Added the `at_content()` method to the `Sequence` class.
- Applied `__slots__` to `SeqInterval` and `SeqEntry` to reduce memory overhead.

### Analysis & Visualization
- Enhanced `plot_kmer()` to support k-mer heatmaps across multiple sequences.
- Refactored `AnalysisResult` into an abstract base class.
- Added concrete result types:
  - `IntervalResult`
  - `KmerResult`
- Results returned by analysis functions (e.g. `kmer()`) can now be visualized directly via a unified `.plot()` interface.

### Quality Assurance
- Numerous minor fixes and internal refinements.
- Comprehensive test coverage (≥ 95%).

## Usage example
#### Creating a sliding window GC chart using **omiBio**:
```python
# Load sequences from FASTA (returns dict[str, Sequence])
seqs: SeqCollections[SeqEntry] = read_fasta("examples/example.fasta")
dna: Sequence = seqs["example"]

# Compute GC content in sliding windows (window=200 bp, step=20 bp)
result: IntervalResult[SeqInterval] = sliding_gc(dna, window=200, step=20)

# Visualize easily
result.plot(show=True)  # or: plot_sliding_gc(result, show=True)
```
Or even a one-liner:
```python
sliding_gc(read_fasta("examples/example.fasta")["example"]).plot(show=True)
```

The above code will produce results like this:

<p align="center">
  <img src="https://raw.githubusercontent.com/LK923/omiBioKit/main/examples/assets/sliding_gc_viz_demo.png" alt="Example" width="800"/>
</p>


#### Using **omiBio**'s Command-line interfaces:
```bash
$ omibio orf find example.fasta --min-length 100
```
The above CLI will produce results like this:
```bash
seq_id       start   end     strand  frame   length
example_2    70      289     -       -2      219
example_16   53      257     +       +3      204
example_13   118     301     +       +2      183
example_4    92      272     -       -1      180
example_2    157     322     +       +2      165
example_5    17      173     -       -1      156
example_16   176     332     -       -1      156
...

```
## Installation / 安装

### From PyPI:
```bash
$ pip install omibio
```

## Requirements

- **Python**: >= 3.12
- **Core dependencies**:
  - `click` (for CLI)
  - `numpy` & `pandas` → analysis/plotting dependencies
  - `matplotlib` & `seaborn` → enables visualization 

For complete project build and dependency configuration, please refer to [`pyproject.toml`](pyproject.toml)

## Code Style

**omiBio** follows [PEP 8](https://peps.python.org/pep-0008/) conventions for Python code.  
All code is automatically formatted and checked using **flake8**.

## License
This project is licensed under the MIT License.

## Things to note
- Most of the code in this project uses 0-based indexes, half-open interval, rather than the 1-based indexes commonly used in biology.
- All code type hints in this project use PEP 585 generic syntax in Python 3.9+.
- This project is still under development and not yet ready for production. Please use it with caution. If you have any suggestions, please contact us:
  - **gmail**: linkaiwen048@gmail.com
  - **qq**: 2658592119
