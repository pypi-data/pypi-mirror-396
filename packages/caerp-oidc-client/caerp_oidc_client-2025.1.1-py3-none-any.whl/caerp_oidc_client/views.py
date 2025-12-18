"""
Login Views overriding default ones and allowing OpenIdConnect connection
"""

import logging
import re
import secrets
from urllib.parse import urlencode

import jwt
import requests
from caerp.utils.rest.apiv1 import Apiv1Resp
from caerp.utils.security.auth import connect_user
from caerp.utils.session import delete_session_from_cookie_value, get_session_id
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPFound,
    HTTPUnauthorized,
)
from pyramid.security import NO_PERMISSION_REQUIRED, forget, remember

from .exceptions import AuthException
from .interfaces import IJwtService
from .models import OidcSession

logger = logging.getLogger("caerp." + __name__)

HTTP_SUCCESS_CODE = (200, 201, 202)

# Motif regex de validation des parametres
PARAM_PATTERN = re.compile(r"^[a-zA-Z0-9-_.]+$")


class OidcLoginView:
    _session_nextpage_key = "oidc.redirect_afterauth"
    _state_key = "oidc.state"
    _nonce_key = "oidc.nonce"
    _idtoken_key = "id_token"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.pyramid_settings = request.registry.settings
        self.jwks_service = request.find_service(IJwtService)
        self.algorithms = self.get_configuration("token_signature_algorithms").split()

    def get_configuration(self, key):
        return self.pyramid_settings[f"oidc.{key}"]

    def get_next_page(self):
        nextpage = self.request.params.get("nextpage")
        if not nextpage:
            nextpage = self.request.session.get(self._session_nextpage_key)
        logger.debug(f"Redirecting to {nextpage}")
        # avoid redirection looping or set default
        if nextpage in [
            None,
            self.request.route_path("login"),
            self.request.route_path("/oidc_callback"),
        ]:
            nextpage = self.request.route_url("index")
        return nextpage

    def success_response(self):
        """
        Return the result to send on successfull authentication
        """
        if self.request.is_xhr:
            result = Apiv1Resp(self.request)
        else:
            result = HTTPFound(
                location=self.get_next_page(),
                headers=self.request.response.headers,
            )
        return result

    def redirect_uri(self):
        return self.request.route_url("/oidc_callback")

    def auth_endpoint_url(self, state, nonce):
        url = self.get_configuration("auth_endpoint_url")
        params = {
            "redirect_uri": self.redirect_uri(),
            "scope": self.get_configuration("scope"),
            "response_type": "code",
            "client_id": self.get_configuration("client_id"),
            "state": state,
            "nonce": nonce,
        }
        url_params = urlencode(params)
        location = f"{url}?{url_params}"
        return location

    def __call__(self):
        logger.debug("Calling the login view")
        if self.request.identity is not None:
            logger.debug("Found an identity")
            return self.success_response()
        else:
            logger.debug("Redirecting to auth_endpoint")
            # First store the next page in the session
            self.request.session[self._session_nextpage_key] = self.get_next_page()

            # store the state
            state = secrets.token_urlsafe(32)
            self.request.session[self._state_key] = state

            # store the nonce
            nonce = secrets.token_urlsafe(32)
            self.request.session[self._nonce_key] = nonce

            return HTTPFound(self.auth_endpoint_url(state, nonce))

    def call_token_endpoint(self, code) -> dict:
        """
        Call the openid connect token endpoint

        :returns: The jsw encrypted id_token
        """
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri(),
            "client_secret": self.get_configuration("client_secret"),
            "client_id": self.get_configuration("client_id"),
        }
        url = self.get_configuration("token_endpoint_url")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        req = requests.post(url, params, headers)

        if req.status_code not in HTTP_SUCCESS_CODE:
            logger.error(f"Request status {req.status_code}")
            raise AuthException(f"Error code {req.status_code}: {req.text}")

        json_result = req.json()

        return json_result

    def _get_id_token_content(self, json_result: dict) -> dict:
        """
        Parse the jwt encrypted id_token and return a dict
        """
        id_token = json_result["id_token"]
        parsed_id_token = self.jwks_service.decode(id_token)

        if self.request.session[self._nonce_key] != parsed_id_token["nonce"]:
            raise AuthException("wrong nonce token")

        self.request.session[self._idtoken_key] = id_token

        result = {
            "expires_in": json_result["expires_in"],
            "token_type": json_result["token_type"],
            "access_token": json_result["access_token"],
            "id_token": parsed_id_token,
        }
        return result

    def _get_user_login(self, id_token):
        """Return the user login from the id_token"""
        return id_token["preferred_username"]

    def _store_session_in_database(self, id_token):
        logger.debug("Storing session in database")
        oidc_sid = id_token.get("sid")
        oidc_sub = id_token.get("sub")

        if oidc_sid:
            oidc_session = OidcSession.get_from_oidc_sid(self.request, oidc_sid)
        elif oidc_sub:
            oidc_session = OidcSession.get_from_oidc_sub(self.request, oidc_sub)
        else:
            oidc_session = None

        if oidc_session is None:
            oidc_session = OidcSession(
                local_session_id=get_session_id(self.request),
            )
            if oidc_sid:
                oidc_session.oidc_sid = oidc_sid
            if oidc_sub:
                oidc_session.oidc_sub = oidc_sub
            self.request.dbsession.add(oidc_session)
        else:
            logger.warn(
                "It's strange, we already have that remote session id in"
                " the database"
            )

    def oidc_callback_view(self):
        """
        Callback called after successfull authentication
        """
        code = self.request.GET.get("code")
        if not code or not PARAM_PATTERN.match(code):
            logger.debug("oidc_callback: invalid or missing code")
            raise HTTPForbidden()

        state = self.request.GET.get("state")
        if (
            not state
            or not PARAM_PATTERN.match(state)
            or self._state_key not in self.request.session
            or state != self.request.session[self._state_key]
        ):
            logger.debug("oidc_callback: invalid or missing state")
            raise HTTPForbidden()
        else:
            try:
                json_result = self.call_token_endpoint(code)

                auth_data = self._get_id_token_content(json_result)["id_token"]
                self._store_session_in_database(auth_data)
            except AuthException as e:
                logger.exception("Erreur d'authentification: %s", str(e))
                raise HTTPForbidden()
            except Exception as e:
                logger.exception("Erreur inattendue: %s", str(e))
                raise HTTPForbidden()

            login = self._get_user_login(auth_data)
            try:
                connect_user(self.request, login)
            except Exception:
                logger.exception("Erreur en connectant le user %s", login)
                raise HTTPUnauthorized()
            remember(self.request, login)
            return self.success_response()

    def logout_view(self):
        """Logout view"""
        forget(self.request)
        self.request.response.delete_cookie("remember_me")
        url = self.get_configuration("logout_endpoint_url")
        url_params = urlencode(
            {
                "post_logout_redirect_uri": self.request.route_url("login"),
                "id_token_hint": self.request.session.pop(self._idtoken_key),
            }
        )
        location = f"{url}?{url_params}"
        return HTTPFound(location)

    def _get_logout_token_from_request(self):
        """Unencrypt the logout_token that can be found in the request"""
        logger.debug("In the get_logout_token_from_request")
        # Get the jwt logout_token content
        logout_token = self.request.POST.get("logout_token")
        logger.debug(logout_token)
        if logout_token is None:
            raise AuthException("Logout token not found in request")
        parsed_logout_token = self.jwks_service.decode(logout_token)

        logger.debug(parsed_logout_token)
        return parsed_logout_token

    def backend_logout_view(self):
        """
        OpenID Connect Back channel logout view

        Receive a application/x-www-form-urlencoded request with a JWT
        logout_token in the POST params
        """
        logger.debug("+ In the backend logout view")
        # Get the jwt token content
        try:
            logout_token = self._get_logout_token_from_request()
        except Exception:
            logger.exception(" - Error parsing logout token")
            raise HTTPBadRequest()
        # Retrieve the OidcSession object
        oidc_sid = logout_token.get("sid")
        oidc_sub = logout_token.get("sub")
        if oidc_sid:
            oidc_session = OidcSession.get_from_oidc_sid(self.request, oidc_sid)
        elif oidc_sub:
            oidc_session = OidcSession.get_from_oidc_sub(self.request, oidc_sub)
        else:
            raise HTTPBadRequest()
        if oidc_session is None:
            raise HTTPBadRequest()
        delete_session_from_cookie_value(self.request, oidc_session.local_session_id)
        self.request.dbsession.delete(oidc_session)
        self.request.response.headerlist.append(("Cache-Control", "no-store"))
        return {}


def includeme(config):
    # creation d'un service IJWKSClientService

    service_path = config.registry.settings.get(
        "oidc.jwks_service", "caerp_oidc_client.services.NoCheckJWKSService"
    )
    service_factory = config.maybe_dotted(service_path)
    service = service_factory(config.registry.settings)
    config.register_service(service, IJwtService)

    config.add_route("/oidc_callback", "/oidc_callback")
    config.add_route("/oidc_backend_logout", "/oidc_backend_logout")

    config.add_view(
        OidcLoginView,
        route_name="login",
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
        xhr=False,
    )
    config.add_view(
        OidcLoginView,
        route_name="login",
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
        xhr=True,
    )
    config.add_view(
        OidcLoginView,
        route_name="apiloginv1",
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
        request_method="GET",
    )
    config.add_view(
        OidcLoginView,
        route_name="logout",
        attr="logout_view",
        permission=NO_PERMISSION_REQUIRED,
    )

    # Custom OpenId connect views
    config.add_view(
        OidcLoginView,
        route_name="/oidc_callback",
        permission=NO_PERMISSION_REQUIRED,
        attr="oidc_callback_view",
        renderer="json",
    )
    config.add_view(
        OidcLoginView,
        route_name="/oidc_backend_logout",
        attr="backend_logout_view",
        request_method="POST",
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
    )
