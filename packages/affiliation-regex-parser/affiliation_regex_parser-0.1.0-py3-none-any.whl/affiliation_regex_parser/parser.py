from __future__ import annotations

import logging
from pathlib import Path
import re
import time
from functools import lru_cache
from typing import Optional, Sequence, Callable

from flashtext import KeywordProcessor

# from affparsmodels.regexparser.city2country import get_country_by_city
from .city2country import CityCountryResolver, get_country_by_city

# import affparsmodels.regexparser.keyword as keyword
from . import keywords_patterns as keyword


from ._version import __version__

from .providers import (
    CityProvider,
    CountryProvider,
    KeywordCityProvider,
    KeywordCountryProvider,
    CachedCityProvider,
    CachedCountryProvider,
    PackagedOrPathExcelCityProvider,
)


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


CITY_STOPWORDS = {
    "of", "and", "for", "in", "on",
    "de", "di", "da", "la", "le", "del", "von", "der"
}


def _norm_txt(s: str) -> str:
    """Normalize text for case/space/period-insensitive comparison."""
    return re.sub(r"\s+", " ", s.strip().rstrip(".")).lower()


def _dedup(seq: Sequence[str]) -> list[str]:
    """Deduplicate strings while preserving order."""
    seen = set()
    out: list[str] = []
    for x in seq:
        nx = _norm_txt(x)
        if nx in seen:
            continue
        seen.add(nx)
        out.append(x)
    return out


def _remove_overlaps(primary_list: Sequence[str], secondary_list: Sequence[str]) -> list[str]:
    """
    Remove items from secondary_list that overlap (substring-wise)
    with any item in primary_list.
    """
    prim_norm = [_norm_txt(x) for x in primary_list]
    out: list[str] = []
    for s in secondary_list:
        sn = _norm_txt(s)
        if any(sn in p or p in sn for p in prim_norm):
            continue
        out.append(s)
    return out


class AffiliationRegexParser:
    """
    Regex-based parser for extracting structured tags from affiliation strings.

    The parser supports country inference from city names using a worldcities
    Excel dataset. The dataset can be either:
      - packaged inside the library, or
      - provided by the user via a filesystem path.
    """

    def __init__(
        self,
        city_provider: Optional[CityProvider] = None,
        country_provider: Optional[CountryProvider] = None,
        worldcities_path: Optional[Path | str] = None,
        infer_country_by_city: Optional[Callable[[str], Optional[str]]] = None,
    ):
        init_start = time.time()

        # --- keyword-based entity lists ---
        self.department_keywords = keyword.get_department_keywords()
        self.faculty_keywords = keyword.get_faculty_keywords()
        self.institute_keywords = keyword.get_institute_keywords()
        self.university_keywords = keyword.get_university_keywords()
        self.org_keywords = keyword.get_org_keywords()
        self.government_keywords = keyword.get_government_keywords()

        # --- providers for city/country keyword extraction ---
        if city_provider is None:
            # city_provider = CachedCityProvider(
            #     PackagedOrPathExcelCityProvider()
            # )
            city_provider = CachedCityProvider(
                KeywordCityProvider(keyword)
            )
        if country_provider is None:
            country_provider = CachedCountryProvider(
                KeywordCountryProvider(keyword)
            )

        self.city_provider = city_provider
        self.country_provider = country_provider

        self.city_keywords = list(self.city_provider.get_cities())
        self.country_keywords = list(self.country_provider.get_countries())
        self.country_alias_map = dict(self.country_provider.get_alias_map())

        # --- build regex patterns & processors ---
        self._build_patterns()
        self.city_processor = self._build_city_processor(tuple(self.city_keywords))

        # --- country inference factory ---
        if infer_country_by_city is not None:
            # User explicitly supplied a function
            self.infer_country_by_city = infer_country_by_city
        else:
            # Build resolver internally (factory)
            resolver = CityCountryResolver(
                excel_path=worldcities_path
            )
            self.infer_country_by_city = resolver.get_country_by_city

        logger.debug(
            "AffiliationRegexParser initialized in %.6f seconds",
            time.time() - init_start
        )


    @staticmethod
    @lru_cache(maxsize=1)
    def _build_city_processor(city_keywords: tuple[str, ...]) -> KeywordProcessor:
        """Build and cache FlashText processor for city extraction."""
        kp = KeywordProcessor(case_sensitive=False)
        for city in city_keywords:
            c = city.strip()
            if len(c) < 3 or c.lower() in CITY_STOPWORDS:
                continue
            kp.add_keyword(c)
        return kp

    def _build_patterns(self) -> None:
        """Compile all regex patterns used for extraction."""
        joined_dep = "|".join(map(re.escape, self.department_keywords))
        joined_fac = "|".join(map(re.escape, self.faculty_keywords))
        joined_inst = "|".join(map(re.escape, self.institute_keywords))
        joined_uni = "|".join(map(re.escape, self.university_keywords))
        joined_org = "|".join(map(re.escape, self.org_keywords))
        joined_gov = "|".join(sorted(map(re.escape, self.government_keywords), key=len, reverse=True))

        self.dep_pattern = rf"[^,;]*(?:{joined_dep})[^,;]*"
        self.uni_pattern = rf"[^,;]*(?:{joined_uni})[^,;]*"
        self.fac_pattern = rf"(?:^|[,;]\s*)((?:{joined_fac})[^,;\n]*)"
        self.inst_pattern = (
            rf"(?:^|[,;]\s*)((?:(?:[A-Z]{{2,10}}|[A-Z][a-z]{{2,20}})\s+){{0,3}}"
            rf"(?:{joined_inst})[^,;\n]*)"
        )
        self.org_pattern = (
            rf"(?:^|[,;]\s*)((?:(?:[A-Z][A-Za-z&'’.-]{{1,30}})\s+){{0,5}}"
            rf"(?:{joined_org})[^,;\n]*)"
        )
        self.gov_pattern = rf"(?:^|[,;]\s*)((?:{joined_gov})[^,;\n]*)"

        self.postal_pattern = (
            r"\b\d{5}(?:-\d{4})?\b"
            r"|\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b"
            r"|\b[A-Z]{1,2}\d[A-Z0-9]?\s?\d[A-Z]{2}\b"
            r"|\b\d{4,6}\b"
        )
        self.email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"

    def parse(self, affiliation: str) -> dict:
        """
        Parse an affiliation string and extract structured components.
        """
        # Input validation
        if affiliation is None:
            logger.error("Affiliation cannot be None")
            raise ValueError("Affiliation cannot be None")
        if not isinstance(affiliation, str):
            logger.error("Affiliation must be a string, got %s", type(affiliation).__name__)
            raise TypeError("Affiliation must be a string")

        affiliation = affiliation.strip()
        if not affiliation:
            logger.error("Affiliation string is empty after stripping")
            raise ValueError("Affiliation string cannot be empty")

        start_time = time.time()

        # --- Regex-based extraction ---
        departments = [d.strip() for d in re.findall(self.dep_pattern, affiliation, re.IGNORECASE)]
        faculties = [f.strip() for f in re.findall(self.fac_pattern, affiliation, re.IGNORECASE)]
        institutes = [i.strip() for i in re.findall(self.inst_pattern, affiliation, re.IGNORECASE)]
        universities = [u.strip() for u in re.findall(self.uni_pattern, affiliation, re.IGNORECASE)]
        organizations = [
            o.strip() for o in re.findall(self.org_pattern, affiliation, re.IGNORECASE)
            if o.strip() not in universities
        ]
        government_entities = [g.strip() for g in re.findall(self.gov_pattern, affiliation, re.IGNORECASE)]
        emails = re.findall(self.email_pattern, affiliation, re.IGNORECASE)
        postcodes = re.findall(self.postal_pattern, affiliation)

        # --- City extraction ---
        city_t0 = time.time()
        cities = self.city_processor.extract_keywords(affiliation)
        city_time = time.time() - city_t0

        # --- Country extraction ---
        countries: list[str] = []
        seen = set()
        for c in sorted(self.country_keywords, key=len, reverse=True):
            c_norm = c.strip()
            if not c_norm:
                continue
            if re.search(rf"\b{re.escape(c_norm)}\b", affiliation, re.IGNORECASE):
                key = c_norm.lower()
                if key not in seen:
                    countries.append(c_norm)
                    seen.add(key)

        # Infer country from city if needed
        if not countries and cities:
            try:
                inferred_countries = set()
                for city in cities:
                    inferred = self.infer_country_by_city(city)
                    if inferred:
                        inferred_countries.add(inferred)
                if inferred_countries:
                    countries = list(inferred_countries)
                    logger.debug("Inferred countries from cities: %s", countries)
            except Exception as e:
                logger.warning("infer_country_by_city failed: %s", str(e))

        # --- De-duplication and precedence: gov > inst > org ---
        institutes = _dedup(institutes)
        organizations = _dedup(organizations)
        government_entities = _dedup(government_entities)

        institutes = _remove_overlaps(government_entities, institutes)
        organizations = _remove_overlaps(government_entities, organizations)
        organizations = _remove_overlaps(institutes, organizations)

        # --- Normalize country names using alias map ---
        countries_official: list[str] = []
        _seen = set()
        for c in countries:
            key = c.strip().lower().strip(".")
            official = self.country_alias_map.get(key, c)
            if official not in _seen:
                countries_official.append(official)
                _seen.add(official)

        # --- Unknown segments ---
        found_values = set(
            item
            for sublist in [
                departments, faculties, institutes, universities,
                organizations, government_entities, cities,
                countries_official, postcodes, emails
            ]
            for item in sublist
        )

        segments: list[str] = []
        for part in affiliation.split(";"):
            segments.extend([s.strip() for s in part.split(",") if s.strip()])

        unknown: list[str] = []
        for seg in segments:
            seg_norm = re.sub(r"[.\s]+$", "", seg.strip())
            if (
                seg_norm
                and seg_norm not in found_values
                and not re.match(self.email_pattern, seg_norm, re.IGNORECASE)
                and not seg_norm.isdigit()
            ):
                has_partial = any(
                    seg_norm.lower() in val.lower() or val.lower() in seg_norm.lower()
                    for val in found_values
                )
                if not has_partial:
                    unknown.append(seg_norm)

        elapsed = time.time() - start_time
        logger.info(
            "Affiliation parsing completed. Version: %s, Total time: %.6f seconds, City time: %.6f seconds",
            __version__, elapsed, city_time
        )

        return {
            "departments": departments,
            "faculties": faculties,
            "institutes": institutes,
            "universities": universities,
            "organizations": organizations,
            "government_entities": government_entities,
            "cities": cities,
            "countries": countries_official,
            "postcodes": postcodes,
            "emails": emails,
            "unknown": unknown,
            "text": affiliation,
        }
