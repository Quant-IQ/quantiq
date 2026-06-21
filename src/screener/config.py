"""
Screener configuration — named, savable filter sets.

Owner: GT
File: src/screener/config.py
Phase: Phase-3
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

VALID_LOGIC_MODES = {"AND", "OR"}


@dataclass
class ScreenerConfig:
	"""A named, re-runnable screener definition.

	Args:
		name (str): Unique screener name, e.g. ``"oversold_largecap"``.
			Used as the cache key in ``screener/cache.py``.
		conditions (List[Dict[str, Any]]): List of condition dicts, each
			with keys ``metric``, ``operator``, ``value`` — same shape
			``ScreeningEngine.evaluate_ticker`` expects.
		logic_mode (str): ``"AND"`` or ``"OR"``. Defaults to ``"AND"``.
		description (str): Human-readable description of intent.
		universe (List[str]): Ticker names to run the screener against
			(keys into ``ticker_map.TICKER_MAP``). Empty list means
			"caller supplies the universe at run time".

	Raises:
		ValueError: If ``name`` is empty, ``logic_mode`` is invalid, or
			any condition dict is missing a required key.
	"""

	name: str
	conditions: List[Dict[str, Any]] = field(default_factory=list)
	logic_mode: str = "AND"
	description: str = ""
	universe: List[str] = field(default_factory=list)

	def __post_init__(self) -> None:
		if not self.name or not self.name.strip():
			raise ValueError("ScreenerConfig.name must be a non-empty string")

		self.logic_mode = self.logic_mode.upper()
		if self.logic_mode not in VALID_LOGIC_MODES:
			raise ValueError(
				f"logic_mode must be one of {sorted(VALID_LOGIC_MODES)}, "
				f"got {self.logic_mode!r}"
			)

		for i, cond in enumerate(self.conditions):
			missing = {"metric", "operator", "value"} - set(cond.keys())
			if missing:
				raise ValueError(
					f"condition[{i}] missing required key(s) {missing}: {cond}"
				)

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> "ScreenerConfig":
		"""Build a ScreenerConfig from a plain dict (e.g. loaded from JSON).

		Args:
			data (Dict[str, Any]): Dict with keys matching the dataclass
				fields. ``name`` is required; the rest are optional.

		Returns:
			ScreenerConfig: Validated config instance.

		Raises:
			ValueError: If ``data`` is missing ``name``, or any field
				fails validation in ``__post_init__``.
		"""
		if "name" not in data:
			raise ValueError(f"ScreenerConfig.from_dict missing required field 'name': {data}")

		try:
			return cls(
				name=data["name"],
				conditions=data.get("conditions", []),
				logic_mode=data.get("logic_mode", "AND"),
				description=data.get("description", ""),
				universe=data.get("universe", []),
			)
		except (TypeError, ValueError) as e:
			logger.error("ScreenerConfig.from_dict failed for %s: %s", data, e)
			raise ValueError(f"Invalid ScreenerConfig data: {e}") from e

	def to_dict(self) -> Dict[str, Any]:
		"""Serialize back to a plain dict for JSON persistence."""
		return {
			"name": self.name,
			"conditions": self.conditions,
			"logic_mode": self.logic_mode,
			"description": self.description,
			"universe": self.universe,
		}


if __name__ == "__main__":
	import sys

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		handlers=[logging.StreamHandler(sys.stdout)],
	)

	# Real-world example — build a usable screener config and round-trip it
	# through JSON-shaped dicts. Edge cases live in
	# tests/test_screener_config.py (pytest), not here.
	logger.info("--- ScreenerConfig example run ---")

	cfg = ScreenerConfig(
		name="oversold_largecap",
		conditions=[
			{"metric": "RSI", "operator": "<", "value": 30},
			{"metric": "SMA20", "operator": "<", "value": 2500},
		],
		logic_mode="and",
		description="Large-cap NIFTY names currently oversold on RSI and below SMA20",
		universe=["RELIANCE", "TCS", "HDFCBANK"],
	)
	logger.info("Built config: %s", cfg)

	as_dict = cfg.to_dict()
	logger.info("Serialized to dict: %s", as_dict)

	restored = ScreenerConfig.from_dict(as_dict)
	logger.info("Restored from dict, equal to original: %s", restored == cfg)

	logger.info("--- Example run complete ---")
