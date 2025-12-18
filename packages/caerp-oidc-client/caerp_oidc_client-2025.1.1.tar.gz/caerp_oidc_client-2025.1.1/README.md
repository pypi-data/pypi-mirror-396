# Pyramid Oidc client library for caerp


```python
python setup.py install
```

## Add a client in your OpenId Authentication (e.g: Keycloak)


To configure your open id connect client in a SSO server like Keycloak.

Host : https://caerp.mycae.coop

> **Important** Create a custom realm (don't use the master realm, you'll face serious security problems : all users would have admin rights on Keycloak)

### Add a client

- ClientID : caerp_client_id
- Name : Free choice
- Root URL : https://caerp.mycae.coop
- Home URL : https://caerp.mycae.coop
- Valid Redirect URIs : https://caerp.mycae.coop/*
- Valid post logout redirect URIs : https://caerp.mycae.coop/login
- Web Origins : https://caerp.mycae.coop
- Admin URL : Nothing
- Client Authentication : True
- Authentication Flow : Check the following
   - Standard Flow
   - Direct access grants
- Disable Consent required
- Backchannel logout url : https://caerp.mycae.coop/oidc_backend_logout
- Backchannel logout session required: True


For security reasons, always use HTTPS protocol in URLs. Certificates must be provided by well known authorities.

The REQUESTS_CA_BUNDLE environment variable may be used to specify your custom trusted certificates.


### Retrieve the client secret


In the "Credentials" section of the keycloak client view, retrieve the client's secret (you need it to configure caerp)


## Configure your client : caerp

In your caerp application's ini file

```ini
pyramid.includes = ...
                   caerp_oidc_client.models
```

Later in the same ini file
```ini
caerp.authentification_module=caerp_oidc_client

oidc.client_secret=<Secret token from the OIDC server>
oidc.client_id=caerp_client_id
oidc.scope=openid roles
oidc.auth_endpoint_url=<Keycloak auth endpoint url>
oidc.token_endpoint_url=<Keycloak id token endpoint url>
oidc.logout_endpoint_url=<Keycloak logout endpoint url>
```

## JWKS Token validation

Due to backward compatibility, by default, caerp_oidc_client doesn't validate the JWT token using the JWKS encryption data.

JWKS validation is highly recommended and is mandatory for obvious security reasons when the JWT token is transmitted by a third_party (for example frontend or api gateway).

To configure JWKS Token validation, add the following lines :

```ini
oidc.jwks_service=caerp_oidc_client.services.JWKSService
oidc.jwks_endpoint_url=<Keycloak jwks endpoint url>
oidc.token_signature_algorithms=<use one of HS256 HS384 HS512 RS256 RS384 RS512>
```

Keycloak's url are in the form

https://keycloak/realms/**my custom realm name**/protocol/openid-connect/auth

https://keycloak/realms/**my custom realm name**/protocol/openid-connect/token

https://keycloak/realms/**my custom realm name**/protocol/openid-connect/logout

https://keycloak/realms/**my custom realm name**/protocol/openid-connect/certs


## Some advices for security

- Use HTTPS protocol for endpoints
- Apply security recommandations regardless TLS protocol (e.g [Anssi TLS recommandations](https://cyber.gouv.fr/publications/recommandations-de-securite-relatives-tls))
- Aply security recommandations for web sites (e.g [Recommandations relatives pour la sécurisation des sites web](https://www.ssi.gouv.fr/securisation-sites-web)

