# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module providing the Python client to the HPS APIs."""

import atexit
import logging
import os
import platform
import tempfile
import threading
import warnings
from datetime import datetime, timedelta, timezone

import jwt
import requests
from ansys.hps.data_transfer.client import Client as DataTransferClient
from ansys.hps.data_transfer.client import DataTransferApi

from .authenticate import authenticate, determine_auth_url
from .common.redaction import redact_sensitive_values
from .connection import create_session
from .exceptions import HPSError, raise_for_status
from .warnings import UnverifiedHTTPSRequestsWarning

log = logging.getLogger(__name__)


class Client:
    """Provides the Python client to the HPS APIs.

    This class uses the provided credentials to create and store
    an authorized :class:`requests.Session` object.

    The following alternative authentication workflows are supported
    and evaluated in the order listed:

    - Access token: No authentication is needed.
    - Username and password: The client connects to the OAuth server and
      requests access and refresh tokens.
    - Refresh token: The client connects to the OAuth server and
      requests a new access token.
    - Client credentials: The client authenticates with the ``client_id`` and ``client_secret``
      parameters to obtain a new access token. (A refresh token is not included.)

    Parameters
    ----------
    url : str
        Base path for the server to call. The default is ``'https://127.0.0.1:8443/hps'``.
    username : str, optional
        Username.
    password : str, optional
        Password.
    realm : str, optional
        Keycloak realm. The default is ``'rep'``.
    grant_type : str, optional
        Authentication method. The default is ``'password'``.
    scope : str, optional
        String containing one or more requested scopes. The default is ``'openid'``.
    client_id : str, optional
        Client type. The default is ``'rep-cli'``.
    client_secret : str, optional
        Client secret. The default is ``None``.
    access_token : str, optional
        Access token.
    refresh_token : str, optional
        Refresh token.
    auth_url : str, optional
    all_fields : bool, optional
        Whether to apply the ``fields="all"`` query parameter to all requests so
        that all available fields are returned for the requested resources. The
        default is ``True``.
    verify : Union[bool, str], optional
        If a Boolean, whether to verify the server's TLS certificate. The default
        is ``None`, which disables certificate validation and warns the user about it.
        If a string, the path to the CA bundle to use. For more information,
        see the :class:`requests.Session` documentation.
    disable_security_warnings : bool, optional
        Whether to disable urllib3 warnings about insecure HTTPS requests. The default is ``True``.
        For more information, see urllib3 documentation about TLS warnings.
    auto_refresh_token : bool, optional
        Whether to automatically refresh access token before it expires. The default is ``True``.
    token_refresh_factor : float, optional
        Fraction of the token lifetime at which the first preemptive refresh is
        scheduled. Must be in the open interval ``(0, 1)``. The default is ``0.70``.
    token_refresh_retry_factors : sequence of float, optional
        Strictly increasing fractions in ``(token_refresh_factor, 1)`` used to
        reschedule the refresh after a failed attempt. The default is
        ``(0.80, 0.90, 0.95, 0.98)``.
    token_refresh_loop_interval : float, optional
        Maximum interval, in seconds, between checks of the background token refresh
        loop. The default is ``300``.
    token_storage : str, optional
        Storage location for refreshed tokens. Supported values are ``"memory"``
        (default), ``"disk"``, and ``"keyring"``.
        Use ``"disk"`` or ``"keyring"`` if refreshed tokens must persist across
        process restarts. ``"memory"`` keeps refreshed tokens in-process only.
    token_storage_strict : bool, optional
        Whether to fail fast during client initialization if the selected
        ``token_storage`` backend is unavailable. The default is ``False``.
        When ``False``, keyring backend issues are surfaced as warnings and
        token persistence remains in-memory if persistence fails.

    Attributes
    ----------
    last_token_persistence_result : dict | None
        Diagnostic information for the most recent refresh-token persistence
        attempt. The dict contains ``requested_storage``, ``storage_used``,
        ``fallback_used``, ``persisted``, ``path``, and ``error`` fields.
        The value is ``None`` before the first refresh attempt.

    Examples
    --------
    Create a client object and connect to HPS with a username and password.

    >>> from ansys.hps.client import Client
    >>> cl = Client(
    ...     url="https://localhost:8443/hps",
    ...     username="repuser",
    ...     password="repuser"
    ... )

    Create a client object and connect to HPS with a refresh token.

    >>> cl = Client(
    ...     url="https://localhost:8443/hps",
    ...     username="repuser",
    ...     refresh_token="eyJhbGciOiJIUzI1NiIsInR5cC..."
    >>> )

    Create a client object with OIDC tokens and persist refreshed tokens in keyring.

    >>> cl = Client(
    ...     url="https://localhost:8443/hps",
    ...     access_token="eyJhbGciOiJIUzI1NiIsInR5cC...",
    ...     refresh_token="eyJhbGciOiJIUzI1NiIsInR5cC...",
    ...     token_storage="keyring",
    ... )

    """

    def __init__(
        self,
        url: str = "https://127.0.0.1:8443/hps",
        username: str = None,
        password: str = None,
        *,
        realm: str = "rep",
        grant_type: str = None,
        scope="openid",
        client_id: str = "rep-cli",
        client_secret: str = None,
        access_token: str = None,
        refresh_token: str = None,
        all_fields=True,
        verify: bool | str = None,
        disable_security_warnings: bool = True,
        auto_refresh_token: bool = True,
        token_refresh_factor: float = 0.70,
        token_refresh_retry_factors: tuple[float, ...] = (0.80, 0.90, 0.95, 0.98),
        token_refresh_loop_interval: float = 300,
        token_storage: str = "memory",
        token_storage_strict: bool = False,
        **kwargs,
    ):
        """Initialize the Client object."""
        rep_url = kwargs.get("rep_url", None)
        if rep_url is not None:
            url = rep_url
            msg = "The 'rep_url' input argument is deprecated. Use 'url' instead."
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            log.warning(msg)

        auth_url = kwargs.get("auth_url", None)
        if auth_url is not None:
            msg = (
                "The 'auth_url' input argument is deprecated. Use None instead. "
                "New HPS deployments will determine this automatically."
            )
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            log.warning(msg)

        self.url = url
        self.access_token = None
        self.refresh_token = None
        self.username = username
        self.realm = realm
        self.grant_type = grant_type
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        self.verify = verify
        self.data_transfer_url = url + "/dt/api/v1"
        self._token_refresh_thread = None
        self._stop_event = threading.Event()
        if not 0 < token_refresh_factor < 1:
            raise ValueError("token_refresh_factor must be in the open interval (0, 1).")
        if token_refresh_loop_interval <= 0:
            raise ValueError("token_refresh_loop_interval must be positive.")
        retry_factors = tuple(token_refresh_retry_factors)
        prev = token_refresh_factor
        for f in retry_factors:
            if not prev < f < 1:
                raise ValueError(
                    "token_refresh_retry_factors must be strictly increasing and "
                    "in (token_refresh_factor, 1)."
                )
            prev = f
        self.token_refresh_factor = token_refresh_factor
        self.token_refresh_retry_factors = retry_factors
        self.loop_interval = token_refresh_loop_interval
        self._refresh_attempt = 0
        self.token_expires_in = None
        self.token_acquired_date = None
        self.token_refresh_date = None
        self.last_token_persistence_result: dict | None = None
        if token_storage not in ("memory", "disk", "keyring"):
            raise ValueError("token_storage must be one of: 'memory', 'disk', 'keyring'.")
        self.token_storage = token_storage
        self._validate_token_storage_backend(token_storage_strict)

        self._dt_client: DataTransferClient | None = None
        self._dt_api: DataTransferApi | None = None

        if self.verify is None:
            self.verify = False
            msg = (
                f"Certificate verification is disabled. "
                f"Unverified HTTPS requests are made to {self.url}."
            )
            warnings.warn(msg, UnverifiedHTTPSRequestsWarning, stacklevel=2)
            log.warning(msg)

        if disable_security_warnings:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning
            )

        self.auth_url = auth_url

        if not auth_url:
            self.auth_url = determine_auth_url(url, self.verify, realm)

        if access_token:
            log.debug("Authenticate with access token")
            self.access_token = access_token
            self.refresh_token = refresh_token
        else:
            if username and password:
                self.grant_type = "password"
            elif refresh_token:
                self.grant_type = "refresh_token"
            elif client_secret:
                self.grant_type = "client_credentials"

            log.debug(f"Authenticating with '{self.grant_type}' grant type.")

            tokens = authenticate(
                auth_url=self.auth_url,
                grant_type=self.grant_type,
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                refresh_token=refresh_token,
                verify=self.verify,
            )
            self.access_token = tokens["access_token"]
            # client credentials flow does not return a refresh token
            self.refresh_token = tokens.get("refresh_token", None)

            self._update_token_expiry(tokens)

        parsed_username = None
        token = {}
        try:
            token = jwt.decode(self.access_token, options={"verify_signature": False})
        except Exception:
            raise HPSError("Authentication token was invalid.") from None

        # Try to get the standard keycloak name, then other possible valid names
        parsed_username = self._get_username(token)

        if parsed_username is not None:
            if self.username is not None and self.username != parsed_username:
                raise HPSError(
                    f"Username: '{self.username}' and "
                    f"preferred_username: '{parsed_username}' "
                    "from access token do not match."
                )
            self.username = parsed_username

        # For externally supplied access tokens, seed expiry metadata from JWT
        # claims so preemptive refresh can be scheduled consistently.
        if access_token:
            self._initialize_external_token_expiry(token)

        self.session = create_session(
            self.access_token,
            verify=self.verify,
        )
        if all_fields:
            self.session.params = {"fields": "all"}

        # register hook to handle expiring of the refresh token
        self.session.hooks["response"] = [self._auto_refresh_token, raise_for_status]
        self._unauthorized_num_retry = 0
        self._unauthorized_max_retry = 1
        if auto_refresh_token and self.token_refresh_date is not None:
            self._start_token_refresh_thread()

        def exit_handler():
            self._stop_event.set()
            if self._token_refresh_thread is not None:
                self._token_refresh_thread.join(timeout=5)
            if self._dt_client is not None:
                log.info("Stopping the data transfer client gracefully.")
                self._dt_client.stop()

        atexit.register(exit_handler)

    def _get_username(self, decoded_token):
        parsed_username = decoded_token.get("preferred_username", None)
        if not parsed_username:
            parsed_username = decoded_token.get("username", None)
        if not parsed_username:
            parsed_username = decoded_token.get("name", None)

        # Service accounts look like "aud -> service_client_id"
        if not parsed_username:
            if decoded_token.get("oid", "oid_not_found") == decoded_token.get(
                "sub", "sub_not_found"
            ):
                parsed_username = "service_account_" + decoded_token.get("aud", "aud_not_set")
            else:
                raise HPSError("Authentication token had no username.")
        return parsed_username

    def _initialize_external_token_expiry(self, decoded_token):
        """Initialize refresh scheduling from externally provided token claims.

        This allows preemptive refresh to behave consistently when a client is
        created with existing access and refresh tokens (for example from OIDC login).
        """
        if self.refresh_token is None:
            return

        exp = decoded_token.get("exp", None)
        if exp is None:
            return

        now = datetime.now(timezone.utc)
        iat = decoded_token.get("iat", None)
        if iat is not None and exp > iat:
            token_lifetime = int(exp - iat)
            token_acquired_date = datetime.fromtimestamp(iat, timezone.utc)
        else:
            # Fall back to remaining lifetime when iat is unavailable.
            token_lifetime = int(exp - now.timestamp())
            token_acquired_date = now

        if token_lifetime <= 0:
            return

        self.token_expires_in = token_lifetime
        self.token_acquired_date = token_acquired_date
        self._refresh_attempt = 0

        offset = max(1, int(self.token_expires_in * self.token_refresh_factor))
        refresh_date = self.token_acquired_date + timedelta(seconds=offset)
        self.token_refresh_date = max(now, refresh_date)

        log.debug(
            "Initialized refresh schedule from external token, next refresh at %s",
            self.token_refresh_date,
        )

    def _validate_token_storage_backend(self, strict: bool):
        """Validate requested token storage backend availability."""
        from .common.token_storage import _check_storage_backend

        if self.token_storage == "memory":
            return

        if self.token_storage == "disk":
            error = _check_storage_backend("disk")
            if error is None:
                return

            msg = (
                "Disk token storage requested but unavailable: "
                f"{error}. Set token_storage_strict=True to fail fast."
            )
            if strict:
                raise RuntimeError(msg)
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            log.warning(msg)
            return

        if self.token_storage == "keyring":
            error = _check_storage_backend("keyring")
            if error is None:
                return

            msg = (
                "Keyring token storage requested but unavailable: "
                f"{error}. "
                "Set token_storage_strict=True to fail fast."
            )
            if strict:
                raise RuntimeError(msg)
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            log.warning(msg)

    @property
    def rep_url(self) -> str:
        """Deprecated. Use 'url' instead."""
        msg = "The client 'rep_url' property is deprecated. Use 'url' instead."
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        log.warning(msg)
        return self.url

    def initialize_data_transfer_client(self):
        """Initialize the Data Transfer client."""
        if self._dt_client is None:
            try:
                log.info("Starting Data Transfer client.")
                # start Data transfer client
                self._dt_client = DataTransferClient(download_dir=self._get_download_dir())

                self._dt_client.binary_config.update(
                    verbosity=3,
                    debug=False,
                    insecure=True,
                    token=self.access_token,
                    data_transfer_url=self.data_transfer_url,
                )
                self._dt_client.start()

                self._dt_api = DataTransferApi(self._dt_client)
                self._dt_api.status(wait=True)
            except Exception as ex:
                log.debug(ex)
                raise HPSError("Error occurred when starting Data Transfer client.") from ex

    def _get_download_dir(self):
        r"""Return download directory platform dependent.

        Resulting paths:
        `Linux`: /home/user/.ansys/hps/data-transfer/binaries
        `Windows`: C:\\Users\\user\\AppData\\Local\\Ansys\\hps\\data-transfer\\binaries

        Note that on Windows we use AppData\\Local for this,
        not AppData\\Roaming, as the data stored for an application should typically be kept local.

        """
        environment_variable = "LOCALAPPDATA"
        company_folder = "Ansys"
        if platform.uname()[0].lower() != "windows":
            environment_variable = "HOME"
            company_folder = ".ansys"

        home_path = os.environ.get(environment_variable, None)
        if home_path is None:
            # Fallback to the temporary directory
            log.error(
                f"Environment variable {environment_variable} is not set. "
                "Falling back to temporary directory."
            )
            home_path = tempfile.gettempdir()

            log.info(f"Using temporary directory {home_path} for data transfer binaries.")

        return os.path.join(home_path, company_folder, "hps", "data-transfer", "binaries")

    @property
    def auth_api_url(self) -> str:
        """Deprecated. There is no generic auth_api exposed."""
        msg = "The client 'auth_api_url' property is deprecated. \
               There is no generic auth_api exposed."
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        log.warning(msg)
        auth_api_base, _, tail = self.auth_url.partition("realms")
        if tail:
            return auth_api_base
        else:
            log.error("auth_api not valid for non-keycloak implementation")
            return None

    def _start_token_refresh_thread(self):
        """Start a background thread to refresh the access token."""
        if self._token_refresh_thread is not None and self._token_refresh_thread.is_alive():
            return

        self._token_refresh_thread = threading.Thread(
            target=self._periodically_refresh_token,
            name="periodic_token_refresh",
        )
        self._token_refresh_thread.daemon = True
        self._token_refresh_thread.start()

    def _update_token_expiry(self, tokens):
        """Update expiry-related fields from a token response."""
        expires_in = []
        access_expires_in = tokens.get("expires_in", None)
        if access_expires_in is not None:
            log.debug(f"Access token expires in {timedelta(seconds=int(access_expires_in))}")
            expires_in.append(access_expires_in)
        refresh_expires_in = tokens.get("refresh_expires_in", None)
        if refresh_expires_in is not None:
            info = (
                "offline"
                if refresh_expires_in == 0 and "offline_access" in self.scope
                else f"expires in {timedelta(seconds=int(refresh_expires_in))}"
            )
            log.debug(f"Refresh token {info}")
            if refresh_expires_in > 0:
                expires_in.append(refresh_expires_in)
        self.token_expires_in = min(expires_in) if expires_in else None
        if self.token_expires_in is not None:
            log.debug(f"Setting token expiry to {timedelta(seconds=int(self.token_expires_in))}")
        self.token_acquired_date = (
            datetime.now(timezone.utc) if self.token_expires_in is not None else None
        )

        self._refresh_attempt = 0
        if self.token_expires_in is not None:
            offset = max(1, int(self.token_expires_in * self.token_refresh_factor))
            self.token_refresh_date = self.token_acquired_date + timedelta(seconds=offset)
            log.debug(
                "Refresh token set, auto refresh in "
                f"{timedelta(seconds=offset)} ({self.token_refresh_date})"
            )
        else:
            self.token_refresh_date = None

    def _periodically_refresh_token(self):
        """Periodically check if the token needs to be refreshed and refresh it."""
        while not self._stop_event.is_set():
            if self.token_refresh_date is None:
                if self._stop_event.wait(self.loop_interval):
                    break
                continue

            now = datetime.now(timezone.utc)
            if now > self.token_refresh_date:
                log.debug("Attempting preemptive authentication token refresh")
                try:
                    self.refresh_access_token()
                except Exception as ex:
                    self._reschedule_after_failed_refresh(ex)
                continue

            diff = self.token_refresh_date - now
            sleep_time = max(0.1, min(self.loop_interval, diff.total_seconds()))
            if self._stop_event.wait(sleep_time):
                break
        log.debug("Token refresh thread stopped")

    def _reschedule_after_failed_refresh(self, ex):
        """Schedule the next refresh attempt after a failure, if any retries remain."""
        self._refresh_attempt += 1
        if (
            self._refresh_attempt > len(self.token_refresh_retry_factors)
            or self.token_acquired_date is None
            or self.token_expires_in is None
        ):
            log.error(
                "Preemptive token refresh failed and no retries remain: %s. "
                "Falling back to on-demand refresh on the next 401 response.",
                ex,
            )
            self.token_refresh_date = None
            return

        factor = self.token_refresh_retry_factors[self._refresh_attempt - 1]
        offset = max(1, int(self.token_expires_in * factor))
        self.token_refresh_date = self.token_acquired_date + timedelta(seconds=offset)
        log.warning(
            "Preemptive token refresh failed (%s); next attempt scheduled at %.0f%% "
            "of token lifetime (%s).",
            ex,
            factor * 100,
            self.token_refresh_date,
        )

    def _auto_refresh_token(self, response, *args, **kwargs):
        """Provide a callback for refreshing an expired token.

        Automatically refreshes the access token and
        re-sends the request in case of an unauthorized error.
        """
        if (
            response.status_code == 401
            and self._unauthorized_num_retry < self._unauthorized_max_retry
        ):
            log.info("401 authorization error: Trying to get a new access token.")
            self._unauthorized_num_retry += 1
            self.refresh_access_token()
            response.request.headers.update(
                {"Authorization": self.session.headers["Authorization"]}
            )
            if self._dt_client is not None:
                self._dt_client.binary_config.update(token=self.access_token)
            log.debug("Retrying request with updated access token.")
            return self.session.send(response.request)

        self._unauthorized_num_retry = 0
        return response

    def refresh_access_token(self):
        """Request a new access token."""
        if self.grant_type == "client_credentials":
            # Its not recommended to give refresh tokens to client_credentials grant types
            # as per OAuth 2.0 RFC6749 Section 4.4.3, so handle these specially...
            tokens = authenticate(
                auth_url=self.auth_url,
                grant_type="client_credentials",
                scope=self.scope,
                client_id=self.client_id,
                client_secret=self.client_secret,
                verify=self.verify,
            )
        else:
            # Other workflows for authentication generally support refresh_tokens
            if not self.refresh_token:
                raise HPSError("No refresh token available. Re-authentication is required.")
            tokens = authenticate(
                auth_url=self.auth_url,
                grant_type="refresh_token",
                scope=self.scope,
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=self.username,
                refresh_token=self.refresh_token,
                verify=self.verify,
            )
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens.get("refresh_token", None)
        self.session.headers.update({"Authorization": f"Bearer {tokens['access_token']}"})
        self._update_token_expiry(tokens)
        self.last_token_persistence_result = self._persist_refreshed_tokens(tokens)

    def _persist_refreshed_tokens(self, tokens):
        """Persist refreshed tokens and return structured persistence telemetry."""
        result = {
            "requested_storage": self.token_storage,
            "storage_used": self.token_storage,
            "fallback_used": False,
            "persisted": True,
            "path": None,
            "error": None,
        }

        if self.token_storage == "memory":
            return result

        try:
            from .common.token_storage import save_tokens

            path = save_tokens(tokens, self.url, storage=self.token_storage)
            if path is not None:
                result["path"] = str(path)
        except Exception as ex:
            safe_error = redact_sensitive_values(str(ex), tokens)
            log.warning("Unable to persist refreshed tokens to %s: %s", self.token_storage, safe_error)
            result["persisted"] = False
            result["storage_used"] = "memory"
            result["error"] = safe_error

        return result

    @property
    def data_transfer_client(self) -> DataTransferClient:
        """Data Transfer client. If the client is not initialized, it will be started."""
        if self._dt_client is None:
            self.initialize_data_transfer_client()
        return self._dt_client

    @property
    def data_transfer_api(self) -> DataTransferApi:
        """Data Transfer API. If the client is not initialized, it will be started."""
        if self._dt_client is None:
            self.initialize_data_transfer_client()
        return self._dt_api
