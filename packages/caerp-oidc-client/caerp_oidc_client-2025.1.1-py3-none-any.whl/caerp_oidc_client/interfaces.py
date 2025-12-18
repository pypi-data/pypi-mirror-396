from zope.interface import Interface


class IJwtService(Interface):

    def get_signing_key_from_jwt(self, token):
        """
        Retrieve the signing key from the provided JWT token.
        """

    def decode_token(self, token: str) -> dict:
        """
        Parse an openid JWT token and returns the json loaded data.
        In this step, JWKS validation should be performed.
        """
