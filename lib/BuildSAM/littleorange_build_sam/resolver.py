import logging
import os
from sceptre.resolvers import Resolver

from . import sam


def initialiseLogger():

  formatter = logging.Formatter("[%(asctime)s] Command [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  logger = logging.getLogger(__name__)
  logger.handlers = [handler]
  logger.setLevel(logging.INFO)

  return logger


class BuildSAM(Resolver):
  """
  The following instance attributes are inherited from the parent class Resolver.

  Parameters
  ----------
  argument: dict
      The argument of the resolver.
  stack: sceptre.stack.Stack
      The associated stack of the resolver.

  """

  def __init__(self, *args, **kwargs):
    super(BuildSAM, self).__init__(*args, **kwargs)

  def resolve(self):
    """
    resolve is the method called by Sceptre. It should carry out the work
    intended by this resolver. It should return a string to become the
    final value.

    To use instance attribute self.<attribute_name>.

    Examples
    --------
    self.argument
    self.stack

    Returns
    -------
    str Resolved value
    """

    logger = initialiseLogger()

    parameters = self.argument
    profile = self.stack.profile
    region = self.stack.region

    env = os.environ.copy()

    envOverrides = {}
    if region:
      envOverrides["AWS_DEFAULT_REGION"] = region
    if profile:
      envOverrides["AWS_PROFILE"] = profile
    env.update(envOverrides)

    logger.debug(f"Setting environment: {envOverrides}")

    template = sam.build_sam(parameters)

    return template
