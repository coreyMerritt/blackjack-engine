import logging


logging.basicConfig(level=logging.DEBUG, force=True)
logger = logging.getLogger(__name__)

class BlackjackLogger:
  @staticmethod
  def debug(msg) -> None:
    logger.debug(msg)
