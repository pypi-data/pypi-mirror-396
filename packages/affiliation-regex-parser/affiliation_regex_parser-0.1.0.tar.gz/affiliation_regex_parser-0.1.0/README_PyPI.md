
# Affiliation Regex Parser

A lightweight, regex-based Python library for parsing academic author affiliation strings into structured fields (departments, institutes, universities, organizations, cities, countries, emails, postcodes, and unknown segments).

Examples and usage patterns are documented in `cookbook.ipynb`.

## Install

Core install:

```bash
pip install affiliation-regex-parser
````

Optional Excel support (for `worldcities.xlsx`-based city→country inference):

```bash
pip install affiliation-regex-parser[excel]
```

## Features

* Regex-first, deterministic parsing (no ML dependencies).
* Pluggable architecture via providers (e.g., custom city lists, custom inference).
* Optional city→country inference using a world cities dataset.
* Designed for batch parsing (reuse one parser instance).

## Data attribution (worldcities.xlsx)

This project can use a `worldcities.xlsx` dataset sourced from SimpleMaps World Cities (free version), licensed under **Creative Commons Attribution 4.0 (CC BY 4.0)**.

Source:

```text
https://simplemaps.com/data/world-cities
```

If you redistribute the dataset with this package, ensure attribution is preserved per CC BY 4.0.

## Documentation

* See `cookbook.ipynb` for practical examples and common configurations.
* See the docstrings in `AffiliationRegexParser` and provider classes for API details.

## License

MIT License. See `LICENSE`.

## Project status

This package is under active development; the public API aims to remain stable, but outputs may improve over time as patterns and fixtures evolve.


