import base64
import json

import jwt
from jwt import PyJWKClient

from .exceptions import AuthException


class JWKSService:

    def __init__(self, pyramid_settings):
        jwks_url = pyramid_settings.get("oidc.jwks_endpoint_url")
        self.algorithms = pyramid_settings.get(
            "oidc.token_signature_algorithms"
        ).split()
        self.client_id = pyramid_settings.get("oidc.client_id")
        self.client_secret = pyramid_settings.get("oidc.client_secret")
        self.client = PyJWKClient(jwks_url)

    def get_signing_key_from_jwt(self, token):
        return self.client.get_signing_key_from_jwt(token)

    def decode_token(self, token: str) -> dict:
        # contrôle de l'algorithme utilisé
        headers = jwt.get_unverified_header(token)
        alg = headers.get("alg")
        if alg not in self.algorithms:
            raise AuthException(f"Unsupported algorithm: {alg}")

        try:

            if alg in ["RS256", "RS384", "RS512"]:
                # verification les signatures assymétriques
                signing_key = self.get_signing_key_from_jwt(token)
                decoded = jwt.decode(
                    token,
                    key=signing_key.key,
                    algorithms=self.algorithms,
                    audience=self.client_id,
                )
            elif alg in ["HS256", "HS384", "HS512"]:
                # vérification des signatures hmac (basée sur le secret)
                secret_key = self.client_secret
                decoded = jwt.decode(
                    token,
                    key=secret_key,
                    algorithms=self.algorithms,
                    audience=self.client_id,
                )
            elif alg == "none":
                # signatures désactivées
                decoded = jwt.decode(
                    token,
                    key=None,
                    algorithms=self.algorithms,
                    audience=self.client_id,
                )

        except Exception as e:
            raise AuthException("Invalid id_token") from e

        return decoded


class NoCheckJWKSService:
    def __init__(self, pyramid_settings):
        pass

    def decode_token(self, token: str) -> dict:
        """
        Parse an openid JWT token and returns the json loaded data

        :param token: The token to parse id_token or logout_token
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise Exception("Incorrect id token format")

        payload = parts[1]
        padded = payload + "=" * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(padded)
        return json.loads(decoded)
