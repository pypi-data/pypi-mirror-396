
# MagadlalComExam

*Online Exam Tool for [www.magadlal.com](https://www.magadlal.com/)*

## Installation

```bash
pip install MagadlalComExam
```

Or install directly from source:

```bash
git clone https://github.com/makhgal-ganbold/MagadlalComExam
cd MagadlalComExam
pip install .
```

## Usage

```python
import MagadlalComExam as exam

exam.submit_solution(
  uid = "UNIQUE IDENTIFICATION NUMBER",
  expr = """
    Python code
  """
)
```

## Dependencies

* ast
* base64
* gzip
* json
* platform
* re
* requests
* subprocess

Install dependencies:

```bash
pip install requests
```

## Author

[Makhgal Ganbold](https://www.galaa.net/), National University of Mongolia

## Copyright

&copy; 2025 Makhgal Ganbold