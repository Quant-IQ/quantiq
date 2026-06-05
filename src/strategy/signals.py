"""
Signal dataclass definitions representing standard transaction execution nodes.

Owner: AV (Quant Lead) / GT (Co-Lead support)
Phase: Phase 3 shippable target
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Signal:
	"""
	Data transfer object capturing transaction execution parameters with strict post-initialization validation.
	"""

	ticker: str
	action: str  # Must be explicitly configured within {BUY, SELL, HOLD}
	price: float
	reason: str
	timestamp: datetime = None

	def __post_init__(self) -> None:
		"""
		Executes strict schema verification constraints on instance creation.
		"""
		if self.timestamp is None:
			self.timestamp = datetime.now()

		valid_actions = {"BUY", "SELL", "HOLD"}
		if self.action not in valid_actions:
			raise ValueError(
				f"Invalid execution action '{self.action}'. Must be one of {valid_actions}"
			)


# Local verification suite to guarantee validation enforcement
if __name__ == "__main__":
	print("Executing Signal dataclass schema verifications...")

	# Test valid initialization
	valid_node = Signal(
		ticker="M&M.NS", action="BUY", price=2500.50, reason="SMA Crossover detected"
	)
	print(f"Signal node processed successfully: Action -> {valid_node.action}")
	assert valid_node.action == "BUY"

	# Test enforcement of bad actions
	try:
		invalid_node = Signal(
			ticker="M&M.NS",
			action="EXECUTE",
			price=2500.50,
			reason="Broken action token",
		)
		raise AssertionError(
			"Validation Failure: Allowed an unmapped action state to pass."
		)
	except ValueError as error:
		print(f"Exception successfully captured and validated: {str(error)}")
		print("Signal dataclass structural verification tests passed successfully!")
