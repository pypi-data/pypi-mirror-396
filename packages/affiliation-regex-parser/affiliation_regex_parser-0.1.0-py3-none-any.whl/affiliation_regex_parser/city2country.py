from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union
import logging
import importlib.resources as ir


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _lazy_import_pandas():
    """Import pandas lazily to keep base installation lightweight."""
    try:
        import pandas as pd  # type: ignore
    except ImportError as e:
        raise ImportError(
            "Excel-based city-to-country resolution requires optional dependencies. "
            "Install with: pip install affiliation-regex-parser[excel]"
        ) from e
    return pd


@dataclass
class CityCountryResolver:
    """
    Resolve country name(s) for a given city name using the worldcities dataset.

    This resolver supports:
      - A user-supplied Excel path, OR
      - A packaged Excel file shipped within the Python package.

    It loads the dataset once and keeps an in-memory map:
      city_key -> list of unique countries
    """
    excel_path: Optional[Union[str, Path]] = None

    # Packaged file location (inside your installed package)
    package: str = "affiliation_regex_parser"
    package_data_dir: str = "data"
    filename: str = "worldcities.xlsx"

    # Excel reading config
    sheet_name: Union[str, int, None] = 0
    city_col: str = "city"
    country_col: str = "country"

    _map: Optional[Dict[str, List[str]]] = None

    def _get_excel_file_path(self) -> Path:
        """
        Return a filesystem path to the Excel file.

        If excel_path is provided, use it.
        Otherwise, locate the packaged resource via importlib.resources.
        """
        if self.excel_path is not None:
            p = Path(self.excel_path)
            if not p.exists():
                raise FileNotFoundError(f"Excel file not found: {p}")
            return p

        resource = f"{self.package_data_dir}/{self.filename}"
        try:
            res = ir.files(self.package).joinpath(resource)
            # as_file ensures compatibility when resource is inside a wheel/zip
            with ir.as_file(res) as p:
                return Path(p)
        except Exception as e:
            raise FileNotFoundError(
                f"Packaged Excel resource not found or unreadable: {self.package}:{resource}"
            ) from e

    def _ensure_loaded(self) -> None:
        """Load and cache the city->countries map if not already loaded."""
        if self._map is not None:
            return

        pd = _lazy_import_pandas()
        excel_file = self._get_excel_file_path()

        df = pd.read_excel(
            excel_file,
            sheet_name=self.sheet_name,
            usecols=[self.city_col, self.country_col],
        )

        if self.city_col not in df.columns or self.country_col not in df.columns:
            raise ValueError(
                f"Expected columns '{self.city_col}' and '{self.country_col}'. "
                f"Available columns: {list(df.columns)}"
            )

        # Basic cleanup and normalization
        df = df.dropna(subset=[self.city_col, self.country_col]).copy()
        df["city_key"] = df[self.city_col].astype(str).str.strip().str.lower()
        df["country_norm"] = df[self.country_col].astype(str).str.strip()

        # Build city_key -> sorted unique list of countries
        grouped = (
            df.groupby("city_key")["country_norm"]
              .apply(lambda s: sorted(set(s)))
              .to_dict()
        )

        self._map = grouped
        logger.info("Worldcities dataset loaded into memory (rows=%d).", len(df))

    def get_countries_by_city(self, city_name: str) -> List[str]:
        """
        Return a list of country name(s) for a given city name (case-insensitive).

        If not found, returns an empty list.
        """
        self._ensure_loaded()
        assert self._map is not None

        key = str(city_name).strip().lower()
        return list(self._map.get(key, []))

    def get_country_by_city(self, city_name: str) -> Optional[str]:
        """
        Return a single country for a city when the mapping is unambiguous.

        - If no country found: return None
        - If more than one country exists for that city: return None
          (ambiguous city name across multiple countries)
        - If exactly one country: return that country
        """
        countries = self.get_countries_by_city(city_name)
        if not countries:
            return None
        if len(countries) > 1:
            logger.info(
                "Ambiguous city name '%s' (multiple countries=%s). Returning None.",
                city_name, countries
            )
            return None
        return countries[0]


# Convenience function for parser injection (keeps call signature simple)
_default_resolver = CityCountryResolver()


def get_country_by_city(city_name: str) -> Optional[str]:
    """
    Backward-compatible helper that uses the default resolver.

    This is intentionally minimal so it can be used as:
        infer_country_by_city = get_country_by_city
    """
    return _default_resolver.get_country_by_city(city_name)


def get_countries_by_city(city_name: str) -> List[str]:
    """Return all possible countries for the given city name (default resolver)."""
    return _default_resolver.get_countries_by_city(city_name)
