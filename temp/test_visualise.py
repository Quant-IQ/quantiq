import logging

import pandas as pd

from src.data.visualise import plot_ohlc

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def test_plot_ohlc() -> None:
	df = pd.DataFrame(
		{
			"Open": [100, 101, 102, 103, 104],
			"High": [102, 103, 104, 105, 106],
			"Low": [99, 100, 101, 102, 103],
			"Close": [101, 102, 103, 104, 105],
		}
	)

	fig = plot_ohlc(df)

	assert fig is not None

	logger.info("Visualise test passed")


if __name__ == "__main__":
	test_plot_ohlc()
