import logging

class BlackjackLogger:
  logging.basicConfig(level=logging.INFO, force=True)
  logger = logging.getLogger(__name__)

  def debug(self, msg):
    self.logger.debug(msg)

blackjack_logger = BlackjackLogger()
