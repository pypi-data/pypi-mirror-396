import requests

def get_entity_data_by_id(id):
  """
  Requests entity data from SeamlessAccess.org for entity with unique ID `id`.
  Returns JSON (dictionary) containing data.
  """
  response = requests.get(f"https://md.seamlessaccess.org/entities/{id}.json")
  try:
    return response.json()
  except:
    raise Exception(f"invalid response from SeamlessAccess.org for ID {id}")
def find_entity_data_by_name(name):
  """
  Searches SeamlessAccess.org for an institution by name `name`.
  Returns a list of institutions' data.
  """
  response = requests.get(f"https://md.seamlessaccess.org/entities/?q={name}")
  try:
    return response.json()
  except:
    raise Exception(f"invalid response from SeamlessAccess.org for name {name}")
