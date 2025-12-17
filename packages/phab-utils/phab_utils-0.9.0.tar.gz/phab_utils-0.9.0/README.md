# phab-utils

Data processing tools and knowledge base of [Centre for Earth Evolution and Dynamics](https://mn.uio.no/ceed/) and its successor [Centre for Planetary Habitability](https://mn.uio.no/phab/english/).

Original project name was `uio-exoplanet-group`, which later got renamed to `phab-utils` (*on 2025-01-29*).

<!-- MarkdownTOC -->

- [Installing](#installing)
    - [From PyPI](#from-pypi)
    - [From sources](#from-sources)
        - [Building a wheel](#building-a-wheel)
- [Data](#data)
- [Documentation](#documentation)
    - [API](#api)
    - [wiki](#wiki)
- [Tests](#tests)

<!-- /MarkdownTOC -->

## Installing

### From PyPI

``` sh
$ pip install phab-utils
```

If you need an older version from the original `uio-exoplanet-group` package, those are still available [here](https://pypi.org/project/uio-exoplanet-group/#history).

### From sources

``` sh
$ cd /path/to/phab-utils/
$ pip install .
```

Add an `-e` argument, if you'd like to automatically update your locally installed package by pulling from the repository or/and if you intend to modify the sources:

``` sh
$ pip install -e .
```

#### Building a wheel

You can also build a wheel and distribute/install that instead:

``` sh
$ cd /path/to/phab-utils/
$ python -m build
$ pip install ./dist/phab_utils-*.whl
```

## Data

Wherever you see a reference to some data files in documentation, examples, comments or anywhere else, for example some function taking a path like `./data/systems-528n.pkl`, check the [data](https://github.com/retifrav/phab-utils/tree/master/data) folder - chances are, that file will be provided there.

## Documentation

There are two different pieces of documentation.

### API

Located in `documentation`. This is the package API documentation, which is published [here](https://phab.decovar.dev/).

It is generated with [pdoc](https://pdoc.dev):

``` sh
$ pip install pdoc

$ cd /path/to/phab-utils
$ rm -r ./documentation/_deploy/*

$ PHAB_PACKAGE_VERSION=$(git rev-parse --short HEAD) pdoc ./src/phab/utils ./src/phab/tasks \
    --template-directory ./documentation/_templates/ \
    --edit-url="utils=https://github.com/retifrav/phab-utils/blob/master/src/phab/utils/" \
    --edit-url="tasks=https://github.com/retifrav/phab-utils/blob/master/src/phab/tasks/" \
    --output-directory ./documentation/_deploy/
$ cp ./documentation/{favicon.ico,phab.jpg} ./documentation/_deploy/
```

For now it's a blunt deployment of generated HTML, but later it probably will be better to rely on GitHub Actions (*if it won't spend too much of free quota*) by customizing [this workflow](https://github.com/mitmproxy/pdoc/blob/main/.github/workflows/docs.yml).

If you'd like to browse generated documentation locally, you can just open the main `index.html` from `./documentation/_deploy/` in your browser. Alternatively, you can launch a basic Python server:

``` py
$ cd ./documentation/_deploy/
$ python -m http.server 8000
```

and open <http://localhost:8000/>.

### wiki

Located in `wiki`. This is general purpose / technical manuals, articles, notes, etc: how to install/build various tools, dependencies, how to set-up environments and so on.

It is meant to be published somewhere else, but for now it will do being a part of repository. GitHub wikis could've been an option, but those are still quite bad in terms of organizing the content.

## Tests

To run tests:

``` sh
$ pip install pytest

$ python -m pytest ./src/phab/tests/*[^_*].py
$ python -m pytest ./src/phab/tests/databases.py
$ python -m pytest ./src/phab/tests/databases.py -k "test_get_parameters_that_are_double_in_nasa"
```
