import logging

from caerp.models.base.base import DBBASE, default_table_args
from caerp.models.base.mixins import TimeStampedMixin
from sqlalchemy import Column, Integer, String

logger = logging.getLogger(__name__)


class OidcSession(TimeStampedMixin, DBBASE):
    """
    Stores oidc sessions in the database to allow backend logout
    (logout through external rest api calls)
    """

    __tablename__ = "oidc_sessions"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    oidc_sid = Column(String(256))
    local_session_id = Column(String(256))
    oidc_sub = Column(String(256))

    @classmethod
    def get_from_oidc_sid(cls, request, oidc_sid):
        return (
            request.dbsession.query(OidcSession)
            .filter(
                OidcSession.oidc_sid == oidc_sid,
            )
            .first()
        )

    @classmethod
    def get_from_oidc_sub(cls, request, oidc_sub):
        return (
            request.dbsession.query(OidcSession)
            .filter(
                OidcSession.oidc_sub == oidc_sub,
            )
            .first()
        )


def includeme(config):
    logger.debug(" + Including caerp_oidc_client models")
