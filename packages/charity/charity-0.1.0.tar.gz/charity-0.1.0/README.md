# charity

Render a Trie from newline-separated input using Graphviz.

## Installation

```bash
pip install charity
# or from a local checkout
pip install .
```

Graphviz must be installed on your system so the `graphviz` Python package can find the binaries.

## Usage

```bash
cat test/fixtures/simple_input.txt | charity --output trie --format svg --view
```

Options:
- `-o / --output`: Base filename (without extension). Default: `trie`
- `-f / --format`: Graphviz renderer output format (e.g. `pdf`, `png`, `svg`). Default: `pdf`
- `-v / --view`: Open the rendered file after creation.

You can also run the module directly:

```bash
python -m charity < input.txt
```

## Publishing to PyPI

1. Build distributions: `python -m build`
2. Upload: `python -m twine upload dist/*`

Install `build` and `twine` first if needed: `pip install build twine`.
