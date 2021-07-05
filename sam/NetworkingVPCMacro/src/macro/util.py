
class StackParameters(object):

  def __init__(self, parameters):
    self.parameters = parameters

  def resolve(self, parameter):
    if not isinstance(parameter, dict):
      return parameter

    if "Fn::Join" in parameter:
      delimiter, values = parameter["Fn::Join"]
      resolved = self.resolve(delimiter)
      return resolved.join([self.resolve(value) for value in values])

    if "Fn::Split" in parameter:
      delimiter, string = parameter["Fn::Split"]
      resolved = self.resolve(string)
      return resolved.split(delimiter)

    key = None
    if "Ref" in parameter:
      key = parameter["Ref"]
    if "Fn::Ref" in parameter:
      key = parameter["Fn::Ref"]
    if not key:
      raise Exception(
          "Intrinsic functions other than Fn::Ref unsupported for resolving parameter!")

    resolved = self.parameters.get(key)
    if not resolved:
      raise Exception("Intrinsic Fn::Ref must resolve from Parameters!")
    return resolved


def find(collection, searchLambda):
  matches = [element for element in collection if searchLambda(element)]
  if matches == []:
    return None
  return matches[0]
