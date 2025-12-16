import os
import random
import string

from hcs_core.ctxp import profile
from hcs_core.sglib.hcs_client import hcs_client

from hcs_cli.cmds.dev.util import log


def generateRandomAlpha():
    return "_" + "".join(random.choices(string.ascii_uppercase, k=6))


"""
CREATE license-features record record for csp org in V2
Make sure to update the cspOrgId at the top of the file.
Since subscription service is not part of horizonv2-sg group the feature stack will not have the service,
Hence we cannot add subscription to the feature stack, work around is to directly add license to the license-features service
"""


def createLicenseFeatures():
    current_profile = profile.current()
    org_id = os.getenv("ORG_ID", current_profile.csp.orgId)
    data = {
        "licenses": [
            {
                "licenseId": org_id + generateRandomAlpha(),
                "classification": "NAMED",
                "userCount": 50,
                "features": [
                    {"featureName": "VDI_LINUX_DESKTOPS"},
                    {"featureName": "ACCESS_ON_PREM"},
                    {"featureName": "WINDOWS_PHYSICAL_ACCESS"},
                    {"featureName": "VSPHERE"},
                    {"featureName": "LINUX_HOSTED_APPS"},
                    {"featureName": "VM_HOSTED_APPS"},
                    {"featureName": "RDSH_DESKTOPS_APPS"},
                    {"featureName": "INSTANT_CLONE"},
                    {"featureName": "AVAILABILITY_MONITOR"},
                    {"featureName": "AGENT_AUTO_UPDATE_HZE"},
                    {"featureName": "DEPLOY_ONPREM_OR_CLOUD"},
                    {"featureName": "APPMGMT"},
                    {"featureName": "WINDOWS_MULTI_SESSION_DESKTOPS"},
                    {"featureName": "DEPLOY_SINGLE_CLOUD"},
                    {"featureName": "APP_VOLUMES_LCM"},
                    {"featureName": "DEPLOY_HYBRID_MULTI_CLOUD"},
                    {"featureName": "UNIFIED_COMMS"},
                    {"featureName": "CLOUD_MONITORING"},
                    {"featureName": "HELPDESK"},
                    {"featureName": "FULL_CLONE"},
                    {"featureName": "APP_VOLUMES"},
                    {"featureName": "PROTOCOL"},
                    {"featureName": "UNIVERSAL_BROKER"},
                    {"featureName": "DEPLOY_ONPREM_AND_SINGLE_CLOUD"},
                    {"featureName": "ACCESS_CLOUD"},
                    {"featureName": "CLOUD_POD_ARCHITECTURE"},
                    {"featureName": "IMAGE_MANAGEMENT"},
                    {"featureName": "VDI_WINDOWS_DESKTOPS"},
                    {"featureName": "OS_OPTIMIZATION"},
                    {"featureName": "APP_VOLUMES_PKG"},
                    {"featureName": "RECORDING"},
                    {"featureName": "POWER_MANAGEMENT"},
                    {"featureName": "COLLABORATION"},
                    {"featureName": "REST_API_ACCESS"},
                    {"featureName": "VSAN"},
                    {"featureName": "DEM"},
                ],
            }
        ],
        "orgId": org_id,
    }
    log.trivial("Creating license features record for csp org id {}".format(org_id))
    client_id = os.environ.get("CSP_LICENSE_SVC_CLIENT_ID")
    client_secret = os.environ.get("CSP_LICENSE_SVC_CLIENT_SECRET")
    if not client_id:
        print("Using admin service credentials from current profile...")  # which has service permission
        client_id = current_profile.override["admin"]["client-id"]
        client_secret = current_profile.override["admin"]["client-secret"]
    client = hcs_client(
        current_profile.hcs.url,
        {
            "url": current_profile.csp.url,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    response_data = client.post("/license-features/v1/licenses", json=data)
    log.good(f"Successfully created license-features: {response_data}")


if __name__ == "__main__":
    createLicenseFeatures()
