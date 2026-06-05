class DynamicWatchlist:
    pass
import logging

logger = logging.getLogger(__name__)


class DynamicWatchlist:
    def __init__(self, config_name: str):
        self.config_name = config_name
        self.tickers = []

        logger.info(
            f"Created dynamic watchlist for config: {config_name}"
        )

    def refresh(self):
        raise NotImplementedError(
            "Waiting for screener interface"
        )