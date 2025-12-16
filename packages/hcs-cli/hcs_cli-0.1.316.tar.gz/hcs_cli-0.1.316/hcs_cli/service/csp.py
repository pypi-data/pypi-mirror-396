import logging

from hcs_core.ctxp import profile
from hcs_core.sglib import auth
from hcs_core.sglib.ez_client import EzClient

log = logging.getLogger(__name__)

_csp_client = None

# CSP API:
# https://console-stg.cloud.omnissa.com/csp/gateway/ff-service/api/swagger-ui.html#/Feature%20Flags/getOrgFlagsUsingGET


# Use a delay-initialized instance.
# It's because the dependent commands (cmd "query") is a top level command.
# The initialization of the client requires profile initialization.
# Profile initialization for top level commands should be avoided.
def _client():
    global _csp_client
    if not _csp_client:
        url = profile.current().csp.url
        if url.endswith("/"):
            url = url[:-1]
        _csp_client = EzClient(url, oauth_client=auth.oauth_client())
    return _csp_client


class ff:
    @staticmethod
    def list(org_id: str):
        return _client().get(f"/csp/gateway/ff-service/api/orgs/{org_id}/flags")
