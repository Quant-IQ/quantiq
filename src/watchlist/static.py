import logging

logger = logging.getLogger(__name__)


class StaticWatchlist:
    def __init__(self, name: str):
        self.name = name
        self.tickers = []

        logger.info(f"Created watchlist: {name}")

    def add_ticker(self, ticker: str) -> None:
        if ticker in self.tickers:
            logger.info(f"{ticker} already exists in {self.name}")
            return

        self.tickers.append(ticker)
        logger.info(f"Added {ticker} to {self.name}")

    def remove_ticker(self, ticker: str) -> None:
        if ticker in self.tickers:
            self.tickers.remove(ticker)
            logger.info(f"Removed {ticker} from {self.name}")
        else:
            logger.warning(f"{ticker} not found in {self.name}")

    def get_tickers(self) -> list[str]:
        logger.info(f"Retrieved tickers from {self.name}")
        return self.tickers.copy()