import json
from pathlib import Path


def markdown_source(source):
    lines = []
    for line in source.splitlines(True):
        if line.startswith("# "):
            lines.append(line[2:])
        elif line.strip() == "#":
            lines.append("\n")
        else:
            lines.append(line)
    return lines


def build_notebook(script_path):
    cells = []
    current = []
    kind = "code"

    for line in script_path.read_text().splitlines(True):
        if line.startswith("# %% [markdown]") or line.startswith("# %%"):
            if current:
                source = "".join(current)
                cell = {
                    "cell_type": kind,
                    "metadata": {},
                    "source": markdown_source(source) if kind == "markdown" else source.splitlines(True),
                }
                if kind == "code":
                    cell["outputs"] = []
                    cell["execution_count"] = None
                cells.append(cell)

            current = []
            kind = "markdown" if line.startswith("# %% [markdown]") else "code"
        else:
            current.append(line)

    if current:
        source = "".join(current)
        cell = {
            "cell_type": kind,
            "metadata": {},
            "source": markdown_source(source) if kind == "markdown" else source.splitlines(True),
        }
        if kind == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        cells.append(cell)

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


if __name__ == "__main__":
    script = Path(__file__).with_name("train_model.py")
    notebook = Path(__file__).with_name("train_model.ipynb")
    notebook.write_text(json.dumps(build_notebook(script), indent=1))
    print(f"Wrote {notebook}")

