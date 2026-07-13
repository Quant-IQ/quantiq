"""Dhan API authenticated wrapper and rate limiter implementation.

Provides the single entry point for all Dhan API actions across the codebase
with strict adherence to SEBI safety protocols.

Owner: AR | Track: Dev Lead
Phase 4
"""

import logging
import os
import time
from typing import Any, Callable, Dict, List, Optional

from dhanhq.dhanhq import dhanhq as DhanHQ
from dotenv import load_dotenv

# Initialize logging matching repository standards
logger = logging.getLogger(__name__)

# Check for environmental variables at module initialization time
load_dotenv()
DHAN_CLIENT_ID: Optional[str] = os.getenv("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN: Optional[str] = os.getenv("DHAN_ACCESS_TOKEN")

if not DHAN_CLIENT_ID or not DHAN_ACCESS_TOKEN:
	logger.warning(
		"Module-level Warning: DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN environment variables are not set. "
		"API execution calls will fail without valid credentials."
	)


class DhanClientWrapper:
	"""Authenticated wrapper around the dhanhq SDK with rate limiting and retry handling."""

	MAX_ORDERS_PER_SEC: int = 8

	def __init__(self) -> None:
		"""Initializes the underlying Dhan API client using securely loaded credentials."""
		if not DHAN_CLIENT_ID or not DHAN_ACCESS_TOKEN:
			raise ValueError(
				"Cannot initialize Dhan client: Missing credentials in environment."
			)

		self.client: DhanHQ = DhanHQ(
			client_id=DHAN_CLIENT_ID,
			access_token=DHAN_ACCESS_TOKEN,
		)
		self._order_timestamps: List[float] = []

	def _rate_limited_call(
		self, fn: Callable[..., Any], *args: Any, **kwargs: Any
	) -> Any:
		"""Throttles executions to stay strictly below the SEBI 10 orders/sec limit.

		Args:
		    fn (Callable): The underlying Dhan SDK client method to execute.
		    *args (Any): Variable length argument list for the function call.
		    **kwargs (Any): Arbitrary keyword arguments for the function call.

		Returns:
		    Any: The response from the executed function call.
		"""
		now: float = time.time()
		# Slide the window to prune out timestamps older than 1 second
		self._order_timestamps[:] = [t for t in self._order_timestamps if now - t < 1.0]

		if len(self._order_timestamps) >= self.MAX_ORDERS_PER_SEC:
			sleep_time: float = 1.0 - (now - self._order_timestamps[0])
			if sleep_time > 0:
				logger.info(
					"Rate limit window threshold reached. Sleeping for %.2f seconds",
					sleep_time,
				)
				time.sleep(sleep_time)

		self._order_timestamps.append(time.time())
		return fn(*args, **kwargs)

	def execute_api_call(
		self, fn_name: str, *args: Any, **kwargs: Any
	) -> Optional[Dict[str, Any]]:
		"""Wraps all external client interactions with exponential backoff retry and tracking.

		Args:
		    fn_name (str): String name of the method present on the underlying DhanHQ SDK client object.
		    *args (Any): Positional arguments passed directly through to the client method.
		    **kwargs (Any): Keyword arguments passed directly through to the client method.

		Returns:
		    Optional[Dict[str, Any]]: The parsed response payload dictionary or None if all attempts exhaust.
		"""
		fn: Optional[Callable[..., Any]] = getattr(self.client, fn_name, None)
		if not fn:
			logger.error(
				"Requested method '%s' does not exist on the DhanHQ SDK instance.",
				fn_name,
			)
			return None

		backoffs: List[float] = [1.0, 2.0, 4.0]
		max_retries: int = len(backoffs)

		for attempt in range(max_retries + 1):
			try:
				# Direct rate-limited verification hook
				response: Any = self._rate_limited_call(fn, *args, **kwargs)

				# Check for explicit HTTP status mock strings or dictionary responses indicative of a 429
				if isinstance(response, dict):
					status: Optional[str] = response.get("status")
					remarks: str = str(response.get("remarks", "")).lower()

					if status == "FAILURE" and (
						"429" in remarks or "rate limit" in remarks
					):
						if attempt < max_retries:
							wait: float = backoffs[attempt]
							logger.warning(
								"Dhan API hit 429 rate limit. Retrying attempt %d in %.1fs",
								attempt + 1,
								wait,
							)
							time.sleep(wait)
							continue
						else:
							logger.error(
								"Dhan API 429 rate limit errors persisted across all configured retries."
							)
							return None

				return response

			except Exception as e:
				logger.error(
					"Dhan API runtime call failed for %s execution: %s", fn_name, e
				)
				if attempt < max_retries:
					wait = backoffs[attempt]
					logger.warning(
						"Exception caught. Re-attempting connection %d in %.1fs",
						attempt + 1,
						wait,
					)
					time.sleep(wait)
				else:
					logger.error("Dhan API connection attempts fully exhausted.")
					return None
		return None


if __name__ == "__main__":
	# Smoke testing context module execution checks block
	logging.basicConfig(
		level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
	)
	logger.info(
		"Running standard module smoke test check infrastructure layout instantiation..."
	)
	try:
		wrapper = DhanClientWrapper()
		logger.info(
			"Dhan Client Wrapper structural execution instance context cleanly prepared."
		)
	except ValueError as val_err:
		logger.info(
			"Module safely handles context initialization when env parameters are missing: %s",
			val_err,
		)
