import logging


logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

class BlackjackLogger:
  @staticmethod
  def debug(msg) -> None:
    logger.debug(msg)
