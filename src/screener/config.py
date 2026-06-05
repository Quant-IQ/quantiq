from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ScreenerConfig:
	"""
	Screener configuration schema that parses dictionary parameters defensively
	and enforces explicit validation checks.
	"""

	config_name: str
	tickers: List[str]
	technical_filters: Dict[str, Any] = field(default_factory=dict)
	fundamental_filters: Dict[str, Any] = field(default_factory=dict)

	@classmethod
	def from_dict(cls, data_dict: Dict[str, Any]) -> "ScreenerConfig":
		"""
		Parses an input configuration dictionary with explicit schema validation.
		Raises ValueError with the precise missing field name if validation fails.
		"""
		if not data_dict:
			raise ValueError("Configuration data dictionary cannot be empty or None")

		# Explicit mandatory field checking per core backlog specifications
		required_fields = ["config_name", "tickers"]
		for field_name in required_fields:
			if field_name not in data_dict or data_dict[field_name] is None:
				raise ValueError(
					f"Missing required configuration schema field: '{field_name}'"
				)

		# Type validation tracking
		if not isinstance(data_dict["config_name"], str):
			raise ValueError(
				"Schema validation error: 'config_name' must be a valid string identifier"
			)

		if not isinstance(data_dict["tickers"], list):
			raise ValueError(
				"Schema validation error: 'tickers' must be configured as a list of strings"
			)

		return cls(
			config_name=data_dict["config_name"],
			tickers=data_dict["tickers"],
			technical_filters=data_dict.get("technical_filters", {}),
			fundamental_filters=data_dict.get("fundamental_filters", {}),
		)


# Verification test suite to prove validation accuracy
if __name__ == "__main__":
	print("Executing ScreenerConfig structural validation tests...")

	# 1. Test Valid Schema Processing
	valid_input = {
		"config_name": "nifty_auto_momentum",
		"tickers": ["M&M.NS", "TVS.NS"],
		"technical_filters": {"rsi_max": 70, "rsi_min": 30},
		"fundamental_filters": {"pe_max": 40.0},
	}

	config_node = ScreenerConfig.from_dict(valid_input)
	print(f"Valid schema parsed successfully: ID -> '{config_node.config_name}'")
	assert config_node.config_name == "nifty_auto_momentum"

	# 2. Test Invalid/Missing Schema Exceptions
	invalid_input = {
		"tickers": [
			"M&M.NS"
		]  # Explicitly missing the critical 'config_name' key to trigger fallback
	}

	try:
		ScreenerConfig.from_dict(invalid_input)
		raise AssertionError(
			"Validation Failure: Engine allowed an incomplete configuration schema to pass."
		)
	except ValueError as error:
		print(f"Exception successfully caught and validated: {str(error)}")
		assert "config_name" in str(error), (
			"Error string must isolate the missing target field"
		)
		print("Screener configuration validation test passed successfully!")
