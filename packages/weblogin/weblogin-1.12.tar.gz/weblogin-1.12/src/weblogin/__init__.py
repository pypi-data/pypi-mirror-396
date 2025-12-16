import requests

class AuthenticationError(Exception):
  pass
class AutologinHandler:
  """
  An abstract class for a handler for the AutologinSession class.
  """

  def login(self, session, response, args=None, kwargs=None):
    """
    Performs a login based on the response from a request.
    - `session` is an instance of requests.Session, most likely an instance of 
      AutologinSession.
    - `response` is the response of the latest request.
    - `args` and `kwargs` are the options from the latest request, this is so 
      that we can redo that request after logging in.

    Raises an AuthenticationError exception if authentication fails.
    """
    raise NotImplementedError()

  def need_login(self, response):
    """
    Checks a response to determine if logging in is needed,
    returns True if needed.
    """
    raise NotImplementedError()

class AutologinSession(requests.Session):
  """
  Maintains an authenticated session to a web system. This class intercepts any 
  requests made in a requests.Session and ensures that we log in when 
  redirected to the login page.
  """

  def __init__(self, handlers):
    """
    Takes a list of handlers. A handler should derive from AutologinHandler.
    """
    super().__init__()
    self.__handlers = handlers

  def __getstate__(self):
    state = super().__getstate__()
    state["_AutologinSession__handlers"] = self.__handlers
    return state

  def request(self, *args, **kwargs):
    """
    Wrapper around requests.Session.request(...) to check we must log in.
    """
    response = super().request(*args, **kwargs)
    
    for handler in self.__handlers:
      if handler.need_login(response):
        response = handler.login(self, response, args, kwargs)

    return response
