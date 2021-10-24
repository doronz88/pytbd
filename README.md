# Description

Inspired by [tbdswizzler](https://gist.github.com/steventroughtonsmith/9e8ecbd0ab89e7d24ce873a464c5dc83), this simple
python tool for manipulating Apple's `.tbd` format.

# Installation

```shell
python3 -m pip install --user -U pytbd
```

# Usage

```
Usage: pytbd [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  append-arch  appench given arch to all .tbd files
  find-symbol  locate .tbd files where the given symbol is exported from
  json         output given tbd file as json
```
