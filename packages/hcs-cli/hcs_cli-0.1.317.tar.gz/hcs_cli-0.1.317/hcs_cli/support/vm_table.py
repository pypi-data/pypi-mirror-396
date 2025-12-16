import click
from hcs_core.ctxp import util
from hcs_core.util import duration


def format_vm_table(data):
    for d in data:
        updatedAt = d.get("updatedAt")
        if not updatedAt:
            updatedAt = d["createdAt"]

        v = duration.stale(updatedAt)
        if duration.from_now(updatedAt).days >= 1:
            v = click.style(v, fg="bright_black")
        d["stale"] = v

        util.colorize(
            d,
            "lifecycleStatus",
            {
                "DELETING": "bright_black",
                "ERROR": "red",
                "PROVISIONING": "bright_blue",
                "PROVISIONED": "green",
                "MAINTENANCE": "bright_yellow",
                "CUSTOMIZING": "bright_blue",
                "AGENT_UPDATING": "bright_yellow",
                "AGENT_REINSTALLING": "bright_yellow",
            },
        )

        util.colorize(
            d,
            "powerState",
            {
                "PoweredOn": "green",
                "PoweringOn": "bright_blue",
                "PoweredOff": "bright_black",
                "PoweringOff": "bright_blue",
                "Unknown": "red",
            },
        )

        util.colorize(
            d,
            "agentStatus",
            {
                "AVAILABLE": "green",
                "ERROR": lambda d: "bright_black" if d["powerState"] != "PoweredOn" else "red",
                "UNAVAILABLE": lambda d: "bright_black" if d["powerState"] != "PoweredOn" else "red",
            },
        )

        util.colorize(
            d,
            "sessionPlacementStatus",
            {
                "AVAILABLE": "green",
                "UNAVAILABLE": lambda d: "bright_black" if d["powerState"] != "PoweredOn" else "red",
                "QUIESCING": "bright_blue",
            },
        )

    fields_mapping = {}
    if data and "templateId" in data[0]:
        fields_mapping = {"templateId": "Template", "templateType": "Type"}

    fields_mapping |= {
        "id": "Id",
        "lifecycleStatus": "Status",
        "stale": "Stale",
        "powerState": "Power",
        "agentStatus": "Agent",
        "haiAgentVersion": "Agent Version",
        "sessionPlacementStatus": "Session",
        "vmFreeSessions": "Free Session",
    }
    return util.format_table(data, fields_mapping)
