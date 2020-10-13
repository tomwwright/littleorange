import boto3
import hashlib
from sceptre.resolvers import Resolver, ResolvableProperty
import typing
from . import util


class UploadS3(Resolver):
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
    super(UploadS3, self).__init__(*args, **kwargs)

  def resolveArguments(self):
    resolved = {}
    parameters = typing.cast(typing.Mapping, self.argument)
    for k in parameters:
      v = parameters[k]
      if isinstance(v, Resolver):
        if v.stack == None:
          v.stack = self.stack
        resolved[k] = v.resolve()
      else:
        resolved[k] = v

    return resolved

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

    parameters = self.resolveArguments()
    profile = self.stack.profile
    region = self.stack.region

    session = boto3.Session(region_name=region, profile_name=profile)
    s3 = session.client("s3")

    body = parameters["Content"]
    bucket = parameters["Bucket"]
    contentHash = hashlib.md5(body.encode("utf-8")).hexdigest()
    key = contentHash
    if "Key" in parameters:
      key = f"{parameters['Key']}/{key}"
    url = f"https://{bucket}.s3.amazonaws.com/{key}"

    logger.info(f"Uploading as: {url}")

    s3.put_object(
        Body=body.encode("utf-8"),
        Bucket=bucket,
        Key=key
    )

    return url
