from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence, Optional, Union
from pathlib import Path
import importlib.resources as ir


class CityProvider(Protocol):
    """A provider that returns a list of city names."""
    def get_cities(self) -> Sequence[str]:
        raise NotImplementedError


class CountryProvider(Protocol):
    """A provider that returns country keywords and an alias mapping."""
    def get_countries(self) -> Sequence[str]:
        raise NotImplementedError

    def get_alias_map(self) -> Mapping[str, str]:
        raise NotImplementedError


@dataclass
class KeywordCityProvider:
    """
    City provider backed by your keyword module.
    """
    keyword_module: object

    def get_cities(self) -> Sequence[str]:
        return self.keyword_module.get_city_keywords()


@dataclass
class KeywordCountryProvider:
    """
    Country provider backed by your keyword module.
    """
    keyword_module: object

    def get_countries(self) -> Sequence[str]:
        return self.keyword_module.get_country_keywords()

    def get_alias_map(self) -> Mapping[str, str]:
        return self.keyword_module.get_country_alias_map()


@dataclass
class CachedCityProvider:
    """Cache wrapper so cities are loaded only once."""
    provider: CityProvider
    _cache: Optional[Sequence[str]] = None

    def get_cities(self) -> Sequence[str]:
        if self._cache is None:
            self._cache = list(self.provider.get_cities())
        return self._cache


@dataclass
class CachedCountryProvider:
    """Cache wrapper so countries and alias map are loaded only once."""
    provider: CountryProvider
    _countries_cache: Optional[Sequence[str]] = None
    _alias_cache: Optional[Mapping[str, str]] = None

    def get_countries(self) -> Sequence[str]:
        if self._countries_cache is None:
            self._countries_cache = list(self.provider.get_countries())
        return self._countries_cache

    def get_alias_map(self) -> Mapping[str, str]:
        if self._alias_cache is None:
            self._alias_cache = dict(self.provider.get_alias_map())
        return self._alias_cache


@dataclass
class PackagedOrPathExcelCityProvider:
    """
    City provider that reads from:
      1) A user-supplied Excel path, OR
      2) A packaged Excel file shipped within the Python package.

    If excel_path is None, it reads the packaged file (package_data_dir/filename).

    Note: This provider requires optional dependencies: pandas + openpyxl.
    """
    excel_path: Optional[Union[str, Path]] = None

    # Packaged file location (inside your installed package)
    package: str = "affiliation_regex_parser"
    package_data_dir: str = "data"
    filename: str = "worldcities.xlsx"

    # Excel reading config
    sheet_name: Union[str, int, None] = 0
    city_col: str = "city"

    def _read_excel(self):
        """Read Excel from user path if provided, otherwise from packaged data."""
        try:
            import pandas as pd  # local import so base install stays lightweight
        except ImportError as e:
            raise ImportError(
                "Excel support requires optional dependencies. "
                "Install with: pip install affiliation-regex-parser[excel]"
            ) from e

        if self.excel_path is not None:
            p = Path(self.excel_path)
            if not p.exists():
                raise FileNotFoundError(f"Excel file not found: {p}")
            return pd.read_excel(p, sheet_name=self.sheet_name)

        resource = f"{self.package_data_dir}/{self.filename}"
        try:
            excel_res = ir.files(self.package).joinpath(resource)
            with ir.as_file(excel_res) as p:
                return pd.read_excel(p, sheet_name=self.sheet_name)
        except Exception as e:
            raise FileNotFoundError(
                f"Packaged Excel resource not found or unreadable: {self.package}:{resource}"
            ) from e

    def get_cities(self) -> Sequence[str]:
        """Return a stable-order unique list of city names."""
        df = self._read_excel()
        if self.city_col not in df.columns:
            raise ValueError(
                f"Column '{self.city_col}' not found in Excel. Available: {list(df.columns)}"
            )

        cities = (
            df[self.city_col]
            .dropna()
            .astype(str)
            .map(str.strip)
        )
        return list(dict.fromkeys(cities.tolist()))
