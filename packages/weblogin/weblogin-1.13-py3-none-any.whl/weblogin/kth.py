from lxml import html
import requests
import urllib.parse
import weblogin
import weblogin.seamlessaccess as sa

class UGlogin(weblogin.AutologinHandler):
  """
  Login handler (weblogin.AutologinHandler) for UG logins, i.e. through 
  login.ug.kth.se.
  """
  LOGIN_URL = "https://login.ug.kth.se"
  UNAUTH_STATUS_CODES = [
    requests.codes.unauthorized,
    requests.codes.forbidden
  ]
  
  def __init__(self, username, password, login_trigger_url=None,
               rerun_requests=False):
    """
    Creates a login handler that automatically logs into KTH.
    - Requires username and password.
    - Optional `login_trigger_url` is a page that redirects to the login page,
      for instance, the API URLs don't redirect, but the UI URLs do.
    - Optional `rerun_requests` specifies whether we want to rerun the original 
      request that triggered authentication failure.
    """
    super().__init__()
    self.__username = username
    self.__password = password
    self.__login_trigger_url = login_trigger_url
    self.__rerun_requests = rerun_requests
    self.__logging_in = False

  def need_login(self, response):
    """
    Checks a response to determine if logging in is needed,
    returns True if needed
    """
    if self.__logging_in:
      return False

    if response.status_code in self.UNAUTH_STATUS_CODES and \
         "kth.se" in response.url:
      self.__rerun_requests = True
      return True
    elif response.url.startswith(self.LOGIN_URL):
      return True

    return False

  def login(self, session, response, args=[], kwargs={}):
    """
    Performs a login based on the response `response` from a request to session 
    `session`.
    `args` and `kwargs` are the options from the request triggering the login 
    procedure, this is so that we can redo that request after logging in.

    Raises an AuthenticationError exception if authentication fails.
    """
    self.__logging_in = True
    if response.status_code in self.UNAUTH_STATUS_CODES:
      trigger_response = session.get(self.__login_trigger_url)
      login_response = self.login(session, trigger_response)
    else:
      doc_tree = html.fromstring(response.text)
      login_form = doc_tree.xpath("//form[@id='loginForm']")
      if len(login_form) < 1:
        try:
          form = doc_tree.xpath("//form")[0]
        except IndexError:
          raise weblogin.AuthenticationError(
            f"authentication failed, no form found: {response.text}")

        data = {}
        for variable in form.xpath("//input"):
          if variable.name:
            data[variable.name] = variable.value or ""

        action_url = urllib.parse.urljoin(response.url, form.action)

        saml_response = session.request(form.method, action_url, data=data)

        if saml_response.status_code != requests.codes.ok:
          raise weblogin.AuthenticationError(
                              f"SAML error: not OK response: {saml_response.text}")

        final_response = saml_response
      else:
        login_form = login_form[0]
        data = {}

        for variable in login_form.xpath("//input"):
          if variable.value:
            data[variable.name] = variable.value

        data["UserName"] = self.__username if "@ug.kth.se" in self.__username \
                                           else self.__username + "@ug.kth.se"
        data["Password"] = self.__password
        data["Kmsi"] = True

        login_response = session.request(
          login_form.method, f"{self.LOGIN_URL}/{login_form.action}",
          data=data)

        if login_response.status_code != requests.codes.ok:
          raise weblogin.AuthenticationError(
            f"authentication as {self.__username} to {login_response.url} failed: "
            f"{login_response.text}")

        login_doc_tree = html.fromstring(login_response.text)
        login_form = login_doc_tree.xpath("//form[@id='loginForm']")
        if len(login_form) > 0:
          raise weblogin.AuthenticationError(
            f"authentication as {self.__username} failed (redirect to same page), "
            f"probably wrong username or password.")

        final_response = login_response
    self.__logging_in = False

    if self.__rerun_requests and args:
      return session.request(*args, **kwargs)
    return final_response
class SAMLlogin(weblogin.AutologinHandler):
  """
  Login handler (weblogin.AutologinHandler) for SAML at KTH. This will relay to 
  UG (login.ug.kth.se) which handles the password-based authentication.
  """

  def __init__(self, rerun_requests=False):
    """
    Creates a login handler that automatically handles the SAML requests used 
    at KTH.
    """
    super().__init__()
    self.__rerun_requests = rerun_requests
    self.__logging_in = False

  def need_login(self, response, ignore_logging_in=False):
    """
    Checks a response to determine if we should handle a request.
    Returns True if needed.
    """
    if self.__logging_in:
      return False

    return "saml" in response.url and "sys.kth.se" in response.url

  def login(self, session, response, args=[], kwargs={}):
    """
    - Performs an action based on the response `response` from a request to 
      session `session`.
    - `args` and `kwargs` are the options from the request triggering the login 
      procedure, this is so that we can redo that request after logging in.
    - Raises an AuthenticationError exception on fails.
    """
    self.__logging_in = True
    doc_tree = html.fromstring(response.text)
    try:
      form = doc_tree.xpath("//form")[0]
    except IndexError:
      pass
    else:
      data = {}
      for variable in form.xpath("//input"):
        if variable.name:
          data[variable.name] = variable.value or ""

      action_url = urllib.parse.urljoin(response.url, form.action)
      saml_response = session.request(form.method, action_url, data=data)

      if saml_response.status_code != requests.codes.ok:
        raise weblogin.AuthenticationError(
                            f"SAML error: not OK response: {saml_response.text}")
    self.__logging_in = False

    if self.__rerun_requests and args:
      return session.request(*args, **kwargs)
    return saml_response
