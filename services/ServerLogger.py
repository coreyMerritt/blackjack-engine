import logging

logging.basicConfig(level=logging.DEBUG, force=True)
logger = logging.getLogger(__name__)

class ServerLogger:
  @staticmethod
  def debug(msg):
    logger.debug(msg)
