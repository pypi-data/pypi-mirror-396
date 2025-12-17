# Affiliation Regex Parser


A Python library for parsing and structuring academic author affiliation strings using
carefully designed regular expressions and rule-based heuristics.

This project focuses on **deterministic, transparent, and configurable parsing**
of affiliation text commonly found in scholarly metadata, without relying on
machine learning models.

---

## Key Features

- Rule-based parsing using curated regular expressions
- Structured extraction of:
  - departments
  - faculties
  - institutes
  - universities
  - organizations
  - government entities
  - cities
  - countries
  - postcodes
  - emails
- Pluggable architecture via providers (CityProvider, CountryProvider)
- Optional country inference from city names
- Designed for batch processing and reproducible pipelines
- Lightweight default configuration (no Excel dependency required)
- Fully testable and regression-safe


## Design Philosophy

This library is intentionally **not** ML-based.

The goals are:
- deterministic behavior
- explainable outputs
- minimal dependencies
- easy debugging of edge cases
- long-term stability for production and research pipelines

Regexes and keyword lists are treated as first-class assets and are protected
by regression tests.



## Installation

### Base installation (recommended)

```bash
pip install affiliation-regex-parser
````

This installs the core parser with keyword-based city extraction.

### Optional Excel support (for city → country inference)

```bash
pip install affiliation-regex-parser[excel]
```

This enables inference using the `worldcities.xlsx` dataset.



## Usage

All usage patterns (default usage, custom providers, Excel integration,
batch parsing, and testing patterns) are documented in:

📘 **`cookbook.ipynb`**

Please refer to that notebook for practical examples and recommended workflows.



## City and Country Data

### worldcities.xlsx

The project optionally uses the **free version** of the *SimpleMaps World Cities*
dataset for city-to-country inference.

* Source: [https://simplemaps.com/data/world-cities](https://simplemaps.com/data/world-cities)
* License: **Creative Commons Attribution 4.0 (CC BY 4.0)**

When this dataset is included or redistributed, proper attribution to SimpleMaps
is required.

The dataset is used **only** for:

* resolving city names
* inferring countries when no explicit country is present in the affiliation text


## Testing Strategy

The project includes:

* unit tests for core parsing logic
* integration tests for optional Excel-based features
* regression tests driven by real-world affiliation examples

Regression tests ensure that changes to regex patterns or keyword lists
do not unintentionally break existing behavior.


## Project Structure

```
affiliation_regex_parser/
├── parser.py              # Main parser class
├── providers.py           # City/Country provider interfaces and implementations
├── city2country.py        # City → country inference logic
├── patterns_keywords.py   # Keyword lists
├── data/
│   └── worldcities.xlsx   # Optional packaged dataset
tests/
├── unit/
├── integration/
├── regression/
└── fixtures/
```



## License

### Code

This project is licensed under the **MIT License**.

### Data

The `worldcities.xlsx` dataset (if used) is licensed under
**Creative Commons Attribution 4.0 (CC BY 4.0)** by SimpleMaps.


## Acknowledgements

* SimpleMaps for the world cities dataset
* The open academic metadata community for real-world affiliation examples


## Status

This project is under active development.
The public API is considered **stable** for the 0.x series, but feedback and
contributions are welcome.

