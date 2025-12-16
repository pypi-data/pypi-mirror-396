import json
import os
from datetime import datetime

import httpx
import yumako

from hcs_cli.cmds.dev.fs.helper.k8s_util import _fs_kubeconfig
from hcs_cli.cmds.dev.util import log

fail = log.fail


def _http_get(url, type: str = "json", raise_on_error=True):
    response = httpx.get(url)
    log.trivial(f"GET: {url} -> {response.status_code}")
    if response.status_code != 200:
        if raise_on_error:
            fail(f"Failed to fetch {type} from {url}. Status code: {response.status_code}")
        log.trivial(f"GET: {url} -> Status code: {response.status_code}")
        return None
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return response.json()
    else:
        return response.text


def download_kubeconfig(service_name):
    log.trivial(f"Acquiring kubeconfig from Jenkins feature stack pipeline: {service_name}")
    #            https://falcon-jenkins.horizon.services.omnissa.com/view/horizonv2-sg/job/horizonv2-sg_smart-capacity-management-feature/api/json?pretty=true
    page_url = f"https://falcon-jenkins.horizon.services.omnissa.com/view/horizonv2-sg/job/horizonv2-sg_{service_name}-feature/api/json?pretty=true"

    jobs_json = _http_get(page_url)
    jobs = jobs_json.get("jobs")
    if jobs is None:
        log.trivial(json.dumps(jobs_json, indent=2))
        fail(f"No jobs found for service {service_name}. Check if the service name is correct or if the Jenkins job exists.")
    jobs_url = map(lambda x: x["url"], jobs)

    # https://falcon-jenkins.horizon.services.omnissa.com/view/horizonv2-sg/job/horizonv2-sg_smart-capacity-management-feature/job/feature%252Fnanw2/lastSuccessfulBuild/artifact/kubeconfig

    last_job = None
    latest_timestamp = 0
    for job_url in jobs_url:
        api_url = f"{job_url}lastSuccessfulBuild/api/json"
        last_build = _http_get(api_url, raise_on_error=False)
        last_build_timestamp = last_build.get("timestamp", 0)
        if last_build_timestamp > latest_timestamp:
            latest_timestamp = last_build_timestamp
            last_job = job_url
    if not last_job:
        fail(f"No successful builds found for service {service_name}.")
    log.trivial(f"Last successful build URL: {last_job}")
    latest_timestamp_seconds = latest_timestamp / 1000
    latest_datetime = datetime.fromtimestamp(latest_timestamp_seconds)
    human_time = latest_datetime.strftime("%Y-%m-%d %H:%M:%S")
    delta = datetime.now() - latest_datetime
    stale = yumako.time.display(delta)
    log.trivial(f"Last successful build at: {human_time} (stale: {stale})")
    # https://falcon-jenkins.horizon.services.omnissa.com/view/horizonv2-sg/job/horizonv2-sg_smart-capacity-management-feature/job/feature%252Fnanw2/lastSuccessfulBuild/artifact/kubeconfig
    kubeconfig_url = f"{last_job}lastSuccessfulBuild/artifact/kubeconfig"
    kubeconfig = _http_get(kubeconfig_url, raise_on_error=True)

    parent_dir = os.path.dirname(_fs_kubeconfig)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    with open(_fs_kubeconfig, "w+") as f:
        f.write(kubeconfig)
        log.good("Kubeconfig downloaded as " + _fs_kubeconfig)
