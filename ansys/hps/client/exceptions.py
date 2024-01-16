# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

from requests.exceptions import RequestException


class HPSError(RequestException):
    def __init__(self, *args, **kwargs):
        """Base class for all rep related errors.
           Derives from :class:`requests.exceptions.RequestException`.

        Example:
            >>> from ansys.hps.client import HPSError
            >>> from ansys.hps.client.jms import Client
            >>> try:
            >>>     client = Client(url="https://127.0.0.1:8443/rep/",
                                    username="repadmin",
                                    password="wrong_psw")
            >>> except HPSError as e:
            >>>     print(e)
            401 Client Error: invalid_grant for: POST https://127.0.0.1:8443/rep/auth...
            Invalid user credentials
        """
        self.reason = kwargs.pop("reason", None)
        self.description = kwargs.pop("description", None)
        super(HPSError, self).__init__(*args, **kwargs)


class APIError(HPSError):
    def __init__(self, *args, **kwargs):
        """Indicate server side related errors."""
        super(APIError, self).__init__(*args, **kwargs)


class ClientError(HPSError):
    def __init__(self, *args, **kwargs):
        """Indicate client side related errors."""
        super(ClientError, self).__init__(*args, **kwargs)


def raise_for_status(response, *args, **kwargs):
    """Hook function to automatically check HTTP errors.
    Mimics requests.Response.raise_for_status()"""
    if 400 <= response.status_code < 600:

        r_content = {}
        try:
            r_content = response.json()
        except ValueError:
            pass

        reason = r_content.get("title", None)  # jms api
        if not reason:
            reason = r_content.get("error", None)  # auth api
        if not reason:
            reason = response.reason

        description = r_content.get("description", None)  # jms api
        if not description:
            description = r_content.get("error_description", None)  # auth api

        if 400 <= response.status_code < 500:
            error_msg = "%s Client Error: %s for: %s %s" % (
                response.status_code,
                reason,
                response.request.method,
                response.url,
            )
            if description:
                error_msg += f"\n{description}"
            raise ClientError(error_msg, reason=reason, description=description, response=response)
        elif 500 <= response.status_code < 600:
            error_msg = "%s Server Error: %s for: %s %s" % (
                response.status_code,
                reason,
                response.request.method,
                response.url,
            )
            if description:
                error_msg += f"\n{description}"
            raise APIError(error_msg, reason=reason, description=description, response=response)
    return response
