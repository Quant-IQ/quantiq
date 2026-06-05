"""
Standardized Signal dataclass implementation for the QuantIQ ecosystem.

Owner: GT (Co-Lead)
Phase: Phase 2 Strategy Logic Framework
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime

# Initialize module-level logger compliant with CLAUDE.md §17
logger = logging.getLogger(__name__)


@dataclass
class Signal:
	"""Standardized transaction direction marker for strategy triggers.

	Using field(default=None) to maintain strict dataclass ordering standards.
	"""

	direction: str  # 'BUY', 'SELL', or 'HOLD'
	timestamp: datetime = field(default=None)
	action: str = field(default=None)
	ticker: str = field(default="UNKNOWN.NS")


if __name__ == "__main__":
	# Setup standard logging format for smoke test runners
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	)
	logger.info("Starting standalone signals execution validation check...")

	valid_node = Signal(direction="BUY", timestamp=datetime.now(), action="EXECUTE")
	logger.info(
		f"Signal node processed: action={valid_node.action}, direction={valid_node.direction}"
	)
