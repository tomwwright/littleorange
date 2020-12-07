
def find(collection, searchLambda):
  matches = [element for element in collection if searchLambda(element)]
  if matches == []:
    return None
  return matches[0]
