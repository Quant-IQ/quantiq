"""
Discord Alert Webhook Integration Module for QuantIQ.

Sends automated trade execution alerts into designated Discord channels
whenever entry or exit signals fire within the active execution loop.

Owner: GUNEETTAK (Quant / Strategy)
Phase: Phase 4 (Execution Infrastructure)
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict

import requests
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Set up logger instance matching repository protocols
logger = logging.getLogger(__name__)

# Fetch the discord webhook URL from securely managed environment boundaries
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_signal_alert(signal: str, price: float, asset: str = "NIFTY50") -> bool:
	"""
	Send a trade action webhook notification payload cleanly into Discord channels.

	Args:
	    signal (str): The calculated trade signal execution command ('BUY' or 'SELL').
	    price (float): The current calculated execution asset price frame.
	    asset (str): Target stock ticker name (default: 'NIFTY50').

	Returns:
	    bool: True if payload dispatched successfully, False on failures or drops.
	"""
	if not DISCORD_WEBHOOK_URL:
		logger.error(
			"Discord Webhook dispatch aborted: DISCORD_WEBHOOK_URL missing from env config."
		)
		return False

	# Force alert firing threshold logic only on concrete operational vectors
	if signal.upper() not in ["BUY", "SELL"]:
		return False

	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

	# Configure neat rich markdown color embed parameters based on trade direction
	color = (
		3066993 if signal.upper() == "BUY" else 15158332
	)  # Green for BUY, Red for SELL

	payload: Dict[str, Any] = {
		"content": "🚨 **New QuantIQ Strategy Execution Fired** 🚨",
		"embeds": [
			{
				"title": f"Signal Trigger: {signal.upper()}",
				"color": color,
				"fields": [
					{"name": "Asset Ticker", "value": f"`{asset}`", "inline": True},
					{"name": "Execution Price", "value": f"₹{price:,}", "inline": True},
					{
						"name": "Calculation Timestamp",
						"value": f"`{timestamp}`",
						"inline": False,
					},
				],
				"footer": {"text": "QuantIQ Automated Bot Loop Execution Pipeline"},
			}
		],
	}

	try:
		# Fire standard HTTP request securely wrapped within timeouts
		response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)

		if response.status_code == 204:
			logger.info(
				"Successfully dispatched Discord webhook signal alert for %s", signal
			)
			return True

		logger.error(
			"Discord API returned unexpected state code [%s]: %s",
			response.status_code,
			response.text,
		)
		return False

	except Exception as e:
		logger.error(
			"Failed to execute external webhook POST payload connectivity sequence: %s",
			e,
		)
		return False


if __name__ == "__main__":
	# Smoke test structure using logging instead of print to follow project standards
	logging.basicConfig(level=logging.INFO)
	logger.info("Running quick local module smoke alert validation setup...")

	if not DISCORD_WEBHOOK_URL:
		os.environ["DISCORD_WEBHOOK_URL"] = (
			"https://discord.com/api/webhooks/mock_test_url"
		)

	test_run = send_signal_alert(signal="BUY", price=24150.25, asset="RELIANCE.NS")
	logger.info("Module smoke test response state validation status: %s", test_run)
