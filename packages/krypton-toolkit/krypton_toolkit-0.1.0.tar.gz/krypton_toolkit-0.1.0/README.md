# Krypton Toolkit

[![PyPI version](https://badge.fury.io/py/krypton-toolkit.svg)](https://badge.fury.io/py/krypton-toolkit)
[![Python Versions](https://img.shields.io/pypi/pyversions/krypton-toolkit.svg)](https://pypi.org/project/krypton-toolkit/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**Context Engineering Framework for LLMs and Agents.**

Krypton Toolkit helps you extract high-fidelity content from complex documents like PDFs to feed into your Large Language Models.

## Features

- **LLM-based Parsing**: Use state-of-the-art vision models to extract content from PDFs with layout preservation.
- **Generic Parsing**: Fast, rule-based parsing for simpler documents.
- **Smart Splitting**: Split documents into semantic chunks or fixed-size windows with overlap.

## Installation

```bash
pip install krypton-toolkit
```

## Quick Start

### Basic Usage

```python
from krypton.parser import LLMParser, ParsingStrategy

# Initialize parser
parser = LLMParser(model="gpt-4o", api_key="sk-...")

# Parse document
doc = parser.parse("path/to/document.pdf", strategy=ParsingStrategy.VISUAL)

# Access pages
print(f"Parsed {len(doc.pages)} pages.")
```

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.
