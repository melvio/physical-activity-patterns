import logging
from datetime import datetime
import os


def configure_logging(for_file) -> None:
    """

    :return: None
    """
    today: str = datetime.today().strftime('%Y-%m-%d_%H%M%S')
    logging.basicConfig(
        filename=f"./logs/{today}-{os.path.basename(for_file)}.log",
        format='[%(levelname)s] %(asctime)s %(name)s: %(message)s',
        level=logging.DEBUG
    )
