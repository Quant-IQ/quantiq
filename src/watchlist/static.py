import logging

logger = logging.getLogger(__name__)


class StaticWatchlist:
	"""
	A manually curated watchlist of NSE tickers.

	Attributes:
	    name (str): Name of the watchlist.
	    tickers (list[str]): List of stock ticker symbols.

	Example:
	    wl = StaticWatchlist("defence")

	    wl.add_ticker("APOLLO.NS")
	    wl.add_ticker("BEL.NS")

	    wl.remove_ticker("BEL.NS")

	    print(wl.get_tickers())
	"""

	def __init__(self, name: str):
		"""
		Initialize a new watchlist.

		Args:
		    name (str): Watchlist name.
		"""
		self.name = name
		self.tickers: list[str] = []

		logger.info(f"Created watchlist: {name}")

	def add_ticker(self, ticker: str) -> None:
		"""
		Add a ticker to the watchlist.

		Args:
		    ticker (str): NSE ticker symbol.
		"""
		if ticker in self.tickers:
			logger.warning(f"{ticker} already exists in watchlist {self.name}")
			return

		self.tickers.append(ticker)
		logger.info(f"Added {ticker} to {self.name}")

	def remove_ticker(self, ticker: str) -> None:
		"""
		Remove a ticker from the watchlist.

		Args:
		    ticker (str): NSE ticker symbol.
		"""
		if ticker not in self.tickers:
			logger.warning(f"{ticker} not found in watchlist {self.name}")
			return

		self.tickers.remove(ticker)
		logger.info(f"Removed {ticker} from {self.name}")

	def get_tickers(self) -> list[str]:
		"""
		Return a copy of all tickers in the watchlist.

		Returns:
		    list[str]: List of ticker symbols.
		"""
		logger.info(f"Retrieved tickers from {self.name}")
		return self.tickers.copy()
