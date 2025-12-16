from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

# Best-effort list of EEA countries by common names in configs
EEA_COUNTRIES = {
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
}


def _default_patterns_dir() -> Path:
    return Path(__file__).resolve().parent / "data"


@dataclass
class Pattern:
    # title can be string or templated object; we store as Any and pass through
    title: Any
    currency: str
    amount_min: float
    amount_max: float
    amountFormat: int
    types: List[str]
    weight: int = 1000
    prettyTitle: Optional[str] = None
    refundProbability: Optional[float] = None
    refundDelayMinHours: Optional[int] = None
    refundDelayMaxHours: Optional[int] = None
    numberOfOccurrences: Optional[int] = None
    subscriptionFrequencyDays: Optional[int] = None

class PatternsService:
    """Read-only service for transaction patterns."""
    DEFAULT_GENERAL_FILE = "general.yml"
    DEFAULT_EEA_FILE = "eea.yml"
    _ALLOWED_SOURCES = {"general", "eea", "country"}

    def __init__(self, base_dir: str | Path | None = None) -> None:
        override_dir = os.getenv("TRANSACTION_PATTERNS_DIR", "").strip()
        explicit_dir = base_dir
        for candidate in (
            Path(explicit_dir).expanduser() if explicit_dir else None,
            Path(override_dir).expanduser() if override_dir else None,
            _default_patterns_dir(),
        ):
            if not candidate:
                continue
            try:
                normalized = candidate.resolve()
            except OSError:  # pragma: no cover - invalid paths are ignored
                continue
            if normalized.exists() and (normalized / "general.yml").exists():
                self.patterns_dir = normalized
                break
        else:  # pragma: no cover - default dir always exists in package
            self.patterns_dir = _default_patterns_dir()

    def load_general_patterns(self) -> List[Pattern]:
        """Load shared patterns that apply to all countries."""
        return self._load_named_patterns("general")

    def load_eea_patterns(self) -> List[Pattern]:
        """Load the optional EEA supplement."""
        return self._load_named_patterns("eea")

    def load_country_patterns(self, country_name: str) -> List[Pattern]:
        """Load country-specific overrides if available."""
        slug = _slugify_country(country_name)
        if not slug:
            return []
        return self._load_named_patterns(slug)

    def get_country_patterns(self, country: str | None = None) -> List[Pattern]:
        """Return general + optional EEA + country overrides for a country."""
        return self.get_patterns(country=country or "")

    def get_patterns(self, country: str = "", include: str = "") -> List[Pattern]:
        """Return the merged pattern list honoring include filters."""
        include_set = self._parse_include(include)
        country_name = (country or "").strip()

        results: List[Pattern] = []
        if include_set is None or "general" in include_set:
            results.extend(self.load_general_patterns())

        if self._is_eea_country(country_name) and (include_set is None or "eea" in include_set):
            results.extend(self.load_eea_patterns())

        if include_set is None or "country" in include_set:
            results.extend(self.load_country_patterns(country_name))

        return results

    def get_pattern_dicts(self, country: str = "", include: str = "") -> List[Dict[str, Any]]:
        """Return normalized dictionaries ready for JSON serialization."""
        return [self._pattern_to_dict(pattern) for pattern in self.get_patterns(country, include)]

    @lru_cache(maxsize=128)
    def load_patterns_from_file(self, path: Path) -> List[Pattern]:
        if not path.exists():
            return []
        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or []
        except Exception:  # noqa: BLE001
            return []
        results: List[Pattern] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                amountRange = item.get("amountRange", {})
                raw_title: Any = item.get("title", "")
                prettyTitle = item.get("prettyTitle")
                if isinstance(prettyTitle, str):
                    prettyTitle = prettyTitle.strip() or None
                p = Pattern(
                    title=raw_title if isinstance(raw_title, (dict, list)) else str(raw_title).strip(),
                    currency=str(item.get("currency", "")).strip() or "",
                    amount_min=float(amountRange.get("min", 0.0)),
                    amount_max=float(amountRange.get("max", 0.0)),
                    amountFormat=int(item.get("amountFormat", 2)),
                    types=list(item.get("types", []) or []),
                    weight=int(item.get("weight", 1000)),
                    prettyTitle=prettyTitle,
                    refundProbability=(
                        float(refund_prob_val)
                        if (refund_prob_val := item.get("refundProbability")) is not None
                        else None
                    ),
                    refundDelayMinHours=(
                        int(delay_min_val)
                        if (delay_min_val := item.get("refundDelayMinHours")) is not None
                        else None
                    ),
                    refundDelayMaxHours=(
                        int(delay_max_val)
                        if (delay_max_val := item.get("refundDelayMaxHours")) is not None
                        else None
                    ),
                    numberOfOccurrences=(
                        int(occurrences_val)
                        if (occurrences_val := item.get("numberOfOccurrences")) is not None
                        else None
                    ),
                    subscriptionFrequencyDays=(
                        int(frequency_val)
                        if (frequency_val := item.get("subscriptionFrequencyDays")) is not None
                        else None
                    ),
                )
                results.append(p)
            except Exception:  # noqa: BLE001
                continue
        return results

    def _load_named_patterns(self, identifier: str) -> List[Pattern]:
        path = (self.patterns_dir / f"{identifier}.yml").resolve()
        return self.load_patterns_from_file(path)

    def _parse_include(self, include: str) -> Optional[Set[str]]:
        if not include:
            return None
        include_set = {part.strip().lower() for part in include.split(",") if part.strip()}
        if not include_set:
            return None
        invalid = include_set - self._ALLOWED_SOURCES
        if invalid:
            raise ValueError(f"Invalid include values: {sorted(invalid)}")
        return include_set

    @staticmethod
    def _is_eea_country(country_name: str) -> bool:
        return country_name in EEA_COUNTRIES

    @staticmethod
    def _pattern_to_dict(pattern: Pattern) -> Dict[str, Any]:
        return {
            "title": pattern.title,
            "currency": pattern.currency,
            "amountRange": {"min": pattern.amount_min, "max": pattern.amount_max},
            "amountFormat": pattern.amountFormat,
            "types": pattern.types,
            "weight": pattern.weight,
            "prettyTitle": pattern.prettyTitle,
            "refundProbability": pattern.refundProbability,
            "refundDelayMinHours": pattern.refundDelayMinHours,
            "refundDelayMaxHours": pattern.refundDelayMaxHours,
            "numberOfOccurrences": pattern.numberOfOccurrences,
            "subscriptionFrequencyDays": pattern.subscriptionFrequencyDays,
        }

def _slugify_country(country_name: str) -> str:
    return country_name.strip().lower().replace(" ", "_").replace("-", "_")
