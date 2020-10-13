import logging


def initialiseLogger(file, label):

  formatter = logging.Formatter(f"[%(asctime)s] {label} [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  logger = logging.getLogger(__name__)
  logger.handlers = [handler]
  logger.setLevel(logging.INFO)

  return logger
