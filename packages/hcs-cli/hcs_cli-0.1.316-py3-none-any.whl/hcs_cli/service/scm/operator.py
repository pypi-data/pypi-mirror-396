from hcs_core.sglib.client_util import hdc_service_client

from hcs_cli.service.task import TaskModel

_client = hdc_service_client("scm")


def run(org_id: str, name: str, params: str) -> TaskModel:
    url = f"/v1/auto-infra/operators/{name}?"
    if params:
        params = params.replace(" ", "&")
        url += f"&{params}"
    if not params or params.find("org_id") == -1:
        url += f"&org_id={org_id}"
    return _client.post(url, type=TaskModel)


def logs(org_id: str, name: str, limit: int) -> list:
    items = _client.get(f"/v1/auto-infra/operators/{name}/logs?org_id={org_id}&limit={limit}")
    return [TaskModel(**item) for item in items]
