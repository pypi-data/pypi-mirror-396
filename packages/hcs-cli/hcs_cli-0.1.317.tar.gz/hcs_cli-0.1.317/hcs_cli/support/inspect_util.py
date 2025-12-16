import os
import re
from datetime import datetime

import hcs_cli.service as hcs


def _get_query_template(name: str):
    script_dir = os.path.dirname(__file__)
    return os.path.join(script_dir, name)


def inspect_template(org_id: str, template_id: str):
    """Inspect the template."""
    # Get the template
    template = hcs.admin.template.get(id=template_id, org_id=org_id)

    # Get template errors
    template_errors = template.get("reportedStatus", {}).get("errorDetails", [])

    # filter out non-informational errors
    ERROR_CODES_TO_IGNORE = [
        "TEMPLATE_VMS_REACH_LIMIT",
    ]
    template_errors = list(filter(lambda e: e["code"] not in ERROR_CODES_TO_IGNORE, template_errors))

    # Reverse the template_errors array
    template_errors.reverse()

    # Get VM errors in the template
    # Not ideal. https://omnissa.atlassian.net/browse/HV2-138777
    def filter_error_vms(vm):
        return vm["lifecycleStatus"] == "ERROR"

    error_vms = hcs.admin.VM.list(org_id=org_id, template_id=template_id, fn_filter=filter_error_vms)

    # sort by 'updatedAt'
    error_vms.sort(key=lambda vm: datetime.strptime(vm["updatedAt"], "%Y-%m-%dT%H:%M:%S.%f%z"), reverse=True)

    # simplify error messages

    # Extract the last AzureError message
    error_message_pattern = r"AzureError\(code=(.*?), message=(.*?\.)"

    grouped_error_vms = {}

    for vm in error_vms:
        error_message = vm.get("error", "")
        match = re.search(error_message_pattern, error_message)
        if match:
            code = match.group(1)
            message = match.group(2)
        else:
            code = "Unclassified: " + error_message
            message = "<TODO> unclassified"

        holder = grouped_error_vms.get(code)
        if holder:
            holder["count"] += 1
        else:
            holder = {
                "code": code,
                "message": message,
                "count": 1,
                "latest_vm": {
                    "id": vm["id"],
                    "error": vm["error"],
                    "updatedAt": vm["updatedAt"],
                },
            }
            grouped_error_vms[code] = holder

    # sort the 'grouped_error_vms' by count
    error_vm_array = sorted(grouped_error_vms.values(), key=lambda item: item["count"], reverse=True)

    if len(error_vm_array) > 0:
        first = error_vm_array[0]
        summary = f"VM operation error. Code: {first['code']}. {first['message']}"
    elif len(template_errors) > 0:
        first = template_errors[0]
        summary = f"Unclassified template error. Code: {first['code']}. {first['message']}"
    else:
        summary = "<TODO. Not classified. Need to check the log.>"

    # ret = hcs.hoc.es.query(
    #     from_date="-2d",
    #     to_date="now",
    #     template_file=_get_query_template("es_query_templates/query-template-min-free.jsonpt"),
    #     oid=org_id,
    #     tid=template_id,
    # )

    # import json
    # print(json.dumps(ret, indent=2))

    return {"summary": summary, "template_errors": template_errors, "vm_errors": error_vm_array}


def inspect_provider(org_id: str, provider: str):
    return "TODO: inspect provider", 1
