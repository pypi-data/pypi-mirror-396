from lxml import html
from pprint import pprint
import requests
import weblogin
import weblogin.seamlessaccess as sa
import urllib.parse

class SSOlogin(weblogin.AutologinHandler):
  """
  Login handler (weblogin.AutologinHandler) for LADOK logins.
  """
  
  def __init__(self,
      institution,
      test_environment=False,
      vars=None,):
    """
    Creates a login handler that automates the LADOK part of authentication.

    - Requires `institution`. A string identifying the instutution at 
      SeamlessAccess.org.

    - An optional argument `vars` containing keys matching variables of the web 
      page forms whose values should be substituted for the values in the `vars` 
      dictionary. Note that the keys should be casefolded (lower case), since we 
      use `.casefold` to match variable names.
    """
    super().__init__()
    self.__institution = institution
    self.__logging_in = False
    if test_environment:
      self.__base_url = "https://start.test.ladok.se"
    else:
      self.__base_url = "https://start.ladok.se"

    self.__login_url = f"{self.__base_url}/gui/loggain"
    self.__vars = vars or {}

  def need_login(self, response):
    """
    Checks a response to determine if logging in is needed,
    returns True if needed
    """
    if self.__logging_in:
      return False

    if response.status_code == requests.codes.unauthorized \
         and "ladok.se" in response.url:
      return True
    elif response.url.startswith(self.__login_url):
      return True

    return False

  def login(self, session, response, args=None, kwargs=None):
    """
    Performs a login based on the response `response` from a request to session 
    `session`.
    `args` and `kwargs` are the options from the request triggering the login 
    procedure, this is so that we can redo that request after logging in.

    Raises an AuthenticationError exception if authentication fails.
    """
    self.__logging_in = True
    response = session.get(f"{self.__base_url}/Shibboleth.sso/Logout"
                           f"?return={self.__base_url}/gui/auth/swamid/login")
    parsed_url = urllib.parse.urlparse(response.url, allow_fragments=False)
    if "seamlessaccess.org" not in parsed_url.netloc:
      raise weblogin.AuthenticationError(
                      f"seamlessaccess.org not in {parsed_url.netloc}")

    return_url = urllib.parse.unquote(
                            urllib.parse.parse_qs(parsed_url.query)["return"][0])
    try:
      if "{sha1}" in self.__institution:
        sa_data = sa.get_entity_data_by_id(self.__institution)
      else:
        sa_data = sa.find_entity_data_by_name(self.__institution)
        sa_data = sa_data[0]

      entityID = sa_data["entityID"]
    except IndexError:
      raise ValueError(f"{self.__institution} didn't give any match.")
    except KeyError:
      raise Exception(f"SeamlessAccess.org returned unexpected result: {sa_data}")
    if "?" in return_url:
      return_url += f"&entityID={entityID}"
    else:
      return_url += f"?entityID={entityID}"

    ladok_response = session.get(return_url)
    prev = {}
    while "ladok.se" not in \
        urllib.parse.urlparse(ladok_response.url, allow_fragments=False).netloc:
      doc_tree = html.fromstring(ladok_response.text)
      try:
        form = doc_tree.xpath("//form")[0]
      except IndexError:
        raise weblogin.AuthenticationError(f"Got page without any form and "
                                           f"not on LADOK: {ladok_response}")
      data = {}

      for var in form.xpath(".//input"):
        if var.name:
          varname_casefold = var.name.casefold()
          if varname_casefold in self.__vars:
            data[var.name] = self.__vars[varname_casefold]
          else:
            if var.type == "radio":
              if var.checked:
                data[var.name] = var.value
            elif var.name in data:
              if isinstance(data[var.name], list):
                data[var.name].append(var.value)
              else:
                data[var.name] = [data[var.name], var.value]
            else:
              data[var.name] = var.value or ""
      for button in form.xpath("//button"):
        name = button.get("name")
        if button.get("type") == "submit" and "proceed" in name:
          data[name] = ""
      inputs = html.fromstring(ladok_response.text).xpath("//form")[0].inputs.keys()
      prev[ladok_response.url] = inputs

      action_url = urllib.parse.urljoin(ladok_response.url, form.action)
      ladok_response = session.request(form.method, action_url, data=data)

      try:
        new_inputs = \
          html.fromstring(ladok_response.text).xpath("//form")[0].inputs.keys()
      except IndexError:
        new_inputs = None
      if ladok_response.url in prev and new_inputs == prev[ladok_response.url]:
        err = weblogin.AuthenticationError(f"infinite loop for "
                                           f"URL: {action_url}\n"
                                           f"data: {data}")
        err.variables = data
        raise err
    self.__logging_in = False

    if args and response.history:
      return session.request(*args, **kwargs)
    return ladok_response
