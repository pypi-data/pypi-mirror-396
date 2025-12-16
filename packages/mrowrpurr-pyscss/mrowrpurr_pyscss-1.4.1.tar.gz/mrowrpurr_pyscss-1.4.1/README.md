> This is a fork of `pyScss` by @mrowrpurr to add Python 3.13+ support.
>
> Python 3.13+ enforces that global regex flags (like `(?i)`, `(?s)`, `(?m)`) must be at the start of a pattern. pyScss had several patterns with inline flags mid-pattern, which now raise `re.PatternError`. This fork converts them to scoped flag syntax `(?i:...)` or uses `re.compile()` flag arguments.
>
> As of December 2025, `pyScss` has not received updates in 2+ years. This is published so I can use it as a dependency in my own Python 3.13+ projects.

# pyScss, a Scss compiler for Python

[![Build Status](https://travis-ci.org/Kronuz/pyScss.svg?branch=master)](https://travis-ci.org/Kronuz/pyScss)
[![Coverage](https://coveralls.io/repos/Kronuz/pyScss/badge.png)](https://coveralls.io/r/Kronuz/pyScss)

pyScss is a compiler for the [Sass](http://sass-lang.com/) language, a superset of CSS3 that adds programming capabilities and some other syntactic sugar.

## Quickstart

You need Python 2.6+ or 3.3+. PyPy is also supported.

Installation:

```
pip install pyScss
```

Usage:

```
python -mscss < style.scss
```

Python API:

```python
from scss import Compiler
Compiler().compile_string("a { color: red + green; }")
```

## Features

95% of Sass 3.2 is supported. If it's not supported, it's a bug! Please file a ticket.

Most of Compass 0.11 is also built in.

## Further reading

Documentation is in Sphinx. You can build it yourself by running `make html` from within the `docs` directory, or read it on RTD: http://pyscss.readthedocs.org/en/latest/

The canonical syntax reference is part of the Ruby Sass documentation: http://sass-lang.com/docs/yardoc/file.SASS_REFERENCE.html

## Obligatory

Copyright � 2012 German M. Bravo (Kronuz). Additional credits in the documentation.

Licensed under the [MIT license](http://www.opensource.org/licenses/mit-license.php), reproduced in `LICENSE`.
