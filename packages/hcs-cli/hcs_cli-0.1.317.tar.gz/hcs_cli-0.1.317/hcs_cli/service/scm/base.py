import logging

from hcs_core.sglib.client_util import hdc_service_client

log = logging.getLogger(__name__)

_client = hdc_service_client("scm")


def health():
    return _client.get("/v1/health")


def recommend_power_policy(org_id: str, template_id: str):
    return _client.get(f"/v1/templates/{template_id}/power-policies?org_id={org_id}")


def info(org_id: str, param: str):
    return _client.get(f"/v1/auto-infra/info?org_id={org_id}&param={param}")


def template_usage(org_id: str, template_id: str):
    # TODO
    # return _client.get(f"/v1/templates/{template_id}/usage?org_id={org_id}")

    from . import plan

    # plans = plan.list(org_id,
    #           task="com.vmware.horizon.sg.scm.task.CapacityOptimization",
    #           namespace="scm",
    #           meta="",
    #           data=f"templateId={template_id}",
    # )
    # if len(plans) == 0:
    #     return None
    # target = plans[0]

    plan_id = f"CapacityOptimization-{template_id}"
    target = plan.get(id=plan_id, org_id=org_id)
    if not target:
        return None
    return target["meta"]
