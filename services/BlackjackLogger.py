import logging


logging.basicConfig(level=logging.DEBUG, force=True)
logger = logging.getLogger(__name__)

class BlackjackLogger:
  @staticmethod
  def debug(msg) -> None:
    if logger.level == logging.DEBUG:
      logger.debug("\t%s", msg)
