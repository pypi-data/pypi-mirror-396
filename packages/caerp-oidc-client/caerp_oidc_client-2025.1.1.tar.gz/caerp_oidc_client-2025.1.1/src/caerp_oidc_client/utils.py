"""Set of utilities implementing a set of openid connect specs related actions"""

SETTINGS_KEYS = (
    "oidc.client_secret",
    "oidc.scope",
    "oidc.client_id",
    "oidc.auth_endpoint_url",
    "oidc.token_endpoint_url",
    "oidc.logout_endpoint_url",
    "oidc.token_signature_algorithms",
)


def check_settings(pyramid_settings):
    """Check that the app is correctly configured

    :raises Exception: _description_
    """
    for key in SETTINGS_KEYS:
        if key not in pyramid_settings:
            raise Exception(
                "Erreur de configuration, les clés {} "
                "sont requises, il manque {}".format(SETTINGS_KEYS, key)
            )
