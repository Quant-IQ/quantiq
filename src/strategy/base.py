"""
Abstract Base Class framework defining the unified orchestration layout
for all QuantIQ signal generation engines.

Owner: GT (Co-Lead)
Phase: Phase 2 Strategy Logic Framework
"""

import logging
from abc import ABC, abstractmethod
from typing import List

import pandas as pd

# Initialize module-level logger compliant with CLAUDE.md
logger = logging.getLogger(__name__)


class Signal:
	"""Standardized transaction direction marker for strategy triggers."""

	def __init__(self, direction: str, timestamp=None):
		self.direction = direction  # 'BUY' or 'SELL'
		self.timestamp = timestamp


class Strategy(ABC):
	"""Abstract Base Class forcing structural uniform signatures across individual

	quantitative alpha generation systems. Enforces explicit signal parsing methods.
	"""

	def __init__(self, name: str) -> None:
		"""Initializes the base parameters for the designated execution framework.

		Args:
		    name (str): Immutable tracking identifier for the engine instance.
		"""
		self.name = name
		logger.info(f"Initializing strategy core instance: {self.name}")

	@abstractmethod
	def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
		"""Generates trading signals based on the strategy execution logic.

		Args:
		    df (pd.DataFrame): Processed historical OHLCV DataFrame with indicator columns.

		Returns:
		    List[Signal]: Validated transaction direction markers for the input period.

		Raises:
		    NotImplementedError: If subclass does not override this method.
		"""
		raise NotImplementedError("Subclasses must implement generate_signals method.")
