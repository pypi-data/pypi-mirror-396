# snipstr
[![codecov](https://codecov.io/github/imtoopunkforyou/snipstr/graph/badge.svg?token=65OY6J3HP9)](https://codecov.io/github/imtoopunkforyou/snipstr)
[![tests](https://github.com/imtoopunkforyou/snipstr/actions/workflows/tests.yaml/badge.svg)](https://github.com/imtoopunkforyou/snipstr/actions/workflows/tests.yaml)
[![pypi package version](https://img.shields.io/pypi/v/snipstr.svg)](https://pypi.org/project/snipstr)
[![status](https://img.shields.io/pypi/status/snipstr.svg)](https://pypi.org/project/snipstr)
[![pypi downloads](https://img.shields.io/pypi/dm/snipstr.svg)](https://pypi.org/project/snipstr)
[![supported python versions](https://img.shields.io/pypi/pyversions/snipstr.svg)](https://pypi.org/project/snipstr)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![license](https://img.shields.io/pypi/l/snipstr.svg)](https://github.com/imtoopunkforyou/snipstr/blob/main/LICENSE)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)


<p align="center">
  <a href="https://pypi.org/project/snipstr/">
    <img src="https://raw.githubusercontent.com/imtoopunkforyou/snipstr/main/.github/badge/logo.png"
         alt="SnipStr logo">
  </a>
</p>

A lightweight library for easy-to-use text truncation with a friendly interface.

## Installation
```bash
pip install snipstr
```

## Usage
All you need is to import `SnipStr`:
```python
>>> from snipstr import SnipStr
>>> text = 'Python source code and installers are available for download for all versions!'
>>> s = SnipStr(text)
>>> s.snip_to(16).by_side('right').with_replacement_symbol()
>>> str(s)  # 'Python source...'
>>> s.by_side('left')
>>> str(s)  # '...all versions!'
>>> s.snip_to(30)
>>> str(s)  # '... download for all versions!'
>>> s.source  # 'Python source code and installers are available for download for all versions!'
```

### Hashing
`SnipStr` instances are hashable, which allows them to be used as dictionary keys or in sets. The hash is computed based on all instance attributes: `source`, `snip_to`, `by_side`, `with_replacement_symbol`.
```python
>>> from snipstr import SnipStr
>>> s1 = SnipStr('Hello, World!')
>>> s1.snip_to(8).by_side('right').with_replacement_symbol()
>>> s2 = SnipStr('Hello, World!')
>>> s2.snip_to(8).by_side('right').with_replacement_symbol()
>>> hash(s1) == hash(s2)  # True
```

### Collections
Since `SnipStr` is hashable and supports equality, instances can be added to sets and used as dictionary keys:
```python
>>> from snipstr import SnipStr
>>> s1 = SnipStr('Hello')
>>> s1.snip_to(3)
>>> s2 = SnipStr('Hello')
>>> s2.snip_to(3)
>>> s3 = SnipStr('World')
>>> s3.snip_to(3)
# Using in sets (duplicates are removed)
>>> snip_set = {s1, s2, s3}
>>> len(snip_set)  # will return 2
# Using as dictionary keys
>>> snip_dict = {s1: 'first', s3: 'second'}
>>> snip_dict[s2]  # will return 'first', s2 equals s1
```

### Comparison
`SnipStr` instances support rich comparison operations based on their target length:
```python
>>> from snipstr import SnipStr
>>> short = SnipStr('Hello, World!')
>>> short.snip_to(5)
>>> long = SnipStr('Hello, World!')
>>> long.snip_to(10)
>>> short < long  # True
>>> short <= long  # True
>>> long > short  # True
>>> long >= short  # True
```

### Equality
Two `SnipStr` instances are equal if all instance attributes (`source`, `snip_to`, `by_side`, `with_replacement_symbol`) match:
```python
>>> from snipstr import SnipStr
>>> s1 = SnipStr('Hello')
>>> s1.snip_to(3).by_side('right')
>>> s2 = SnipStr('Hello')
>>> s2.snip_to(3).by_side('right')
>>> s3 = SnipStr('Hello')
>>> s3.snip_to(3).by_side('left')
>>> s1 == s2  # will return True
>>> s1 == s3  # Will return False 
```

## License
Curlifier is released under the MIT License. See the bundled [LICENSE](https://github.com/imtoopunkforyou/snipstr/blob/main/LICENSE) file for details.

The logo was created using [Font Meme](https://fontmeme.com/graffiti-creator/).