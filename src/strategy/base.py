"""
Abstract Base Class framework defining the unified orchestration layout
for all QuantIQ signal generation engines.

Owner: GT (Co-Lead)
Phase: Phase 3 Activation target
"""

import os
from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from src.strategy.signals import Signal  # Absolute import tracking path layer


class Strategy(ABC):
	"""
	Abstract Base Class forcing structural uniform signatures across individual
	quantitative alpha generation systems. Enforces explicit signal parsing methods.
	"""

	def __init__(self, name: str) -> None:
		"""
		Initializes the base parameters for the designated execution framework.

		Args:
		    name (str): Immutable tracking identifier for the strategy instance.
		"""
		self._name: str = name

	@property
	def name(self) -> str:
		"""
		Exposes an immutable property layer containing the strategy tracking identifier.

		Returns:
		    str: Operational registration name string.
		"""
		return self._name

	@abstractmethod
	def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
		"""
		Abstract blueprint signature evaluating financial dataframes to compile
		transaction execution logs. Must be explicitly overridden by custom classes.

		Args:
		    df (pd.DataFrame): Processed historical data stream containing metrics.

		Returns:
		    List[Signal]: Array containing validated transaction direction markers.
		"""
		pass


# Verification test suite to enforce non-instantiation rules
if __name__ == "__main__":
	print("Executing Strategy base abstract layout validations...")

	try:
		# Intentionally attempting to instantiate abstract base class to trigger type fallbacks
		broken_instance = Strategy(name="AbstractFallbackEngine")
		raise AssertionError(
			"Validation Failure: Architecture allowed baseline abstract layers to instantiate."
		)
	except TypeError as error:
		print(
			f"Instantiating verification complete. Abstract contract successfully enforced: {str(error)}"
		)
		print("Strategy baseline contract test passed successfully!")
