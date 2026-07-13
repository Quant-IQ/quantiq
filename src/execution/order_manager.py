"""
Manages live order placement via Dhan API.
Scope: v0.0.2 only.
"""


class OrderManager:
	"""Manages live order placement via Dhan API. v0.0.2 only."""

	def place_order(
		self, ticker: str, action: str, quantity: int, price: float
	) -> dict:
		raise NotImplementedError(
			"OrderManager.place_order() is v0.0.2 only. "
			"Use execution/logger.py to log paper trade signals in v0.0.1."
		)

	def cancel_order(self, order_id: str) -> dict:
		raise NotImplementedError("OrderManager.cancel_order() is v0.0.2 only.")

	def get_order_status(self, order_id: str) -> dict:
		raise NotImplementedError("OrderManager.get_order_status() is v0.0.2 only.")

	def get_positions(self) -> list[dict]:
		raise NotImplementedError("OrderManager.get_positions() is v0.0.2 only.")
