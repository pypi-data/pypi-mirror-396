
# pyDMM6500: A Python library for Keithley's DMM6500


⚠️ This package is a work in progress

This project is a Python library for [Keithley's Digital Multimeter 6.5 digits]((https://www.tek.com/en/products/keithley/digital-multimeter/dmm6500)).

It currently supports basic functionnalities such as configuring the multimeter for DC or resistance measurements,
and measurements buffers.


# Installation

```bash
pip install pyDMM6500
```

# Documentation

## Project structure description

```
.
├── LICENSE
├── README.md
├── pyproject.toml
├── src
│   └── pydmm6500
│       ├── __init__.py
│       └── dmm6500.py          DMM6500 Python library source file
└── tests
    ├── integration             Tests performed with a DMM6500
    │   └── test.py
    └── unit                    Unit testing of the package
        └── test.py
```


# References

* [DMM6500 Datasheet](https://www.tek.com/en/datasheet/dmm6500-6-1-2-digit-bench-system-digital-multimeter-datasheet)
* [DMM6500 User’s Manual](https://www.tek.com/en/manual/model-dmm6500-6-1-2-digit-multimeter-user-manual)
* [DMM6500 Reference Manual](https://www.tek.com/en/tektronix-and-keithley-digital-multimeter/dmm6500-manual/model-dmm6500-6-1-2-digit-multimeter-3)

# Publish to PyPi

1. Remove build files

```bash
rm -rf dist build *.egg-info
```

2. Update version in [`pyproject.toml`](pyproject.toml)

```toml
[project]
version = "202x.x.x"
```

3. Build new version

```bash
python3 -m build
```

4. Upload new version to PyPi

```bash
python3 -m twine upload dist/*
```
