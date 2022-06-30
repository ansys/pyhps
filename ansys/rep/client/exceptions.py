# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

from requests.exceptions import RequestException

class REPError(RequestException):
    def __init__(self, *args, **kwargs):
        """Base class for all rep related errors. Derives from :class:`requests.exceptions.RequestException`.
        
        Example:
            >>> from ansys.rep.client import REPError
            >>> from ansys.rep.client.jms import Client
            >>> try:
            >>>     client = Client(rep_url="https://127.0.0.1/dcs/", username="repadmin",  password="wrong_psw")
            >>> except REPError as e:
            >>>     print(e)
            400 Client Error: invalid_grant for: POST https://127.0.0.1/dcs/auth/api/oauth/token
            Invalid "username" or "password" in request.
        """
        self.reason = kwargs.pop('reason', None)
        self.description = kwargs.pop('description', None)
        super(REPError, self).__init__(*args, **kwargs)

class APIError(REPError):
    def __init__(self, *args, **kwargs):
        """Indicate server side related errors."""
        super(APIError, self).__init__(*args, **kwargs)

class ClientError(REPError):
    def __init__(self, *args, **kwargs):
        """Indicate client side related errors."""
        super(ClientError, self).__init__(*args, **kwargs)

def raise_for_status(response, *args, **kwargs):
    """Hook function to automatically check HTTP errors. Mimics requests.Response.raise_for_status()"""
    if 400 <= response.status_code < 600:
        
        r_content = {}
        try:
            r_content = response.json()
        except ValueError:
            pass

        reason = r_content.get("title", None) #dps api
        if not reason:
            reason = r_content.get("error", None) # auth api
        if not reason:
            reason = response.reason

        description = r_content.get("description", None) #dps api
        if not description:
            description = r_content.get("error_description", None) # auth api
        
        if 400 <= response.status_code < 500:
            error_msg = '%s Client Error: %s for: %s %s' % (response.status_code, reason, response.request.method, response.url)
            if description:
                error_msg += f"\n{description}"
            raise ClientError(error_msg, reason=reason, description=description, response=response)
        elif 500 <= response.status_code < 600:
            error_msg = '%s Server Error: %s for: %s %s' % (response.status_code, reason, response.request.method, response.url)
            if description:
                error_msg += f"\n{description}"
            raise APIError(error_msg, reason=reason, description=description, response=response)
    return response