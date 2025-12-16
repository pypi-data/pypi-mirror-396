<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![ReadTheDocs](https://readthedocs.org/projects/assorthead/badge/?version=latest)](https://assorthead.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/assorthead/main.svg)](https://coveralls.io/r/<USER>/assorthead)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/assorthead.svg)](https://anaconda.org/conda-forge/assorthead)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/assorthead)
-->

[![PyPI-Server](https://img.shields.io/pypi/v/assorthead.svg)](https://pypi.org/project/assorthead/)
![Unit tests](https://github.com/BiocPy/assorthead/actions/workflows/pypi-test.yml/badge.svg)

# Assorted C++ headers

**assorthead** vendors an assortment of header-only C++ libraries for compilation of downstream packages.
This centralizes the acquisition and versioning of these libraries for a smoother development experience.
Downstream dependencies include
[**mattress**](https://github.com/tatami-inc/mattress),
[**knncolle**](https://github.com/knncolle/knncolle-py),
[**scranpy**](https://github.com/libscran/scranpy)
and [**singler**](https://github.com/SingleR-inc/singler),
to name a few.

Developers can install **assorthead** via the usual `pip` commands:

```shell
pip install assorthead
```

We add all headers to the compiler's search path using the `include_dirs` argument in the `setup()` command in our `setup.py`:

```python
setup(
    use_scm_version={"version_scheme": "no-guess-dev"},
    ext_modules=[
        Extension(
            "foo.core",
            [
                "src/lib/foo.cpp",
                "src/lib/bar.cpp",
            ],
            include_dirs=[
                assorthead.includes(),
            ],
            language="c++",
            extra_compile_args=[
                "-std=c++17",
            ],
        )
    ],
)
```

See [`extern/manifest.csv`](extern/manifest.csv) for the list of vendored libraries and their versions.
Licenses are available in the directory returned by the `licenses()` function.
