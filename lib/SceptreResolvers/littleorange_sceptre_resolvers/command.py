import logging
import os
from sceptre.resolvers import Resolver
import subprocess
from . import util


class Command(Resolver):
  """
  The following instance attributes are inherited from the parent class Resolver.

  Parameters
  ----------
  argument: str
      The argument of the resolver.
  stack: sceptre.stack.Stack
      The associated stack of the resolver.

  """

  def __init__(self, *args, **kwargs):
    super(Command, self).__init__(*args, **kwargs)

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

    logger = util.initialiseLogger(__name__, self.__class__.__name__)

    command = self.argument
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

    logger.info(f"Running command: '{command}'")

    process = subprocess.run(command, capture_output=True, check=True, env=env, shell=True, text=True)
    if process.returncode != 0:
      raise Exception(f'Command failed with error code {process.returncode}')

    return process.stdout
