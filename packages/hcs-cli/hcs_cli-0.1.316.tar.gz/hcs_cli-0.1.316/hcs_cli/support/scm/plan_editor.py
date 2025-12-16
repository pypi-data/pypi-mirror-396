import json
from datetime import datetime
from os import path

from yumako import template

from hcs_cli.support.scm.html_util import show_html


def _timestamp_to_date(timestamp: int):
    return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%dT%H:%M")


def edit_plan(plan: dict, template_name: str):
    # Start a local server to host plan-editor3.
    file_path = path.join(path.dirname(__file__), "plan-editor.html.template")
    with open(file_path, "r") as f:
        html_template = f.read()

    usage = plan["meta"]
    x_axis = []
    consumed_capacity = []
    spare_capacity = []
    no_spare_error = []
    consumed_capacity_predicated = []
    spare_capacity_predicated = []
    no_spare_error_predicated = []
    optimized_capacity = []
    history = usage["history"]
    prediction = usage["prediction"]
    timeslot_ms = usage["timeslotMs"]
    start_timestamp = history["startTimestamp"]
    for i in range(len(history["maxCapacity"])):
        t = start_timestamp + i * timeslot_ms
        x_axis.append(_timestamp_to_date(t))
        max_capacity = history["maxCapacity"][i]
        min_free = history["minFree"][i]
        consumed_capacity.append(max_capacity - min_free)
        spare_capacity.append(min_free)
        no_spare_error.append(history["noSpare"][i])

    start_timestamp = prediction["startTimestamp"]
    for i in range(len(prediction["maxCapacity"])):
        t = start_timestamp + i * timeslot_ms
        x_axis.append(_timestamp_to_date(t))
        max_capacity = prediction["maxCapacity"][i]
        min_free = prediction["minFree"][i]
        ideal_capacity = prediction["idealCapacity"][i]
        consumed_capacity_predicated.append(ideal_capacity - min_free)
        spare_capacity_predicated.append(min_free)
        optimized_capacity.append(ideal_capacity)
        no_spare_error_predicated.append(prediction["noSpare"][i])
    n = len(consumed_capacity) - 1
    consumed_capacity_predicated = [0] * n + [consumed_capacity[-1]] + consumed_capacity_predicated
    # spare_capacity_predicated = [0] * n + [spare_capacity[-1]] + spare_capacity_predicated
    spare_capacity_predicated = [0] * n + [0] + spare_capacity_predicated
    optimized_capacity = [0] * n + [0] + optimized_capacity
    no_spare_error_predicated = [0] * n + [no_spare_error[-1]] + no_spare_error_predicated

    del usage["history"]
    del usage["prediction"]
    del usage["timeslotMs"]

    html_template = template.replace(
        html_template,
        {
            "PLAN_DATA": json.dumps(plan),
            "x_axis": x_axis,
            "template_name": template_name,
            "consumed_capacity": consumed_capacity,
            "spare_capacity": spare_capacity,
            "no_spare_error": no_spare_error,
            "consumed_capacity_predicated": consumed_capacity_predicated,
            "spare_capacity_predicated": spare_capacity_predicated,
            "no_spare_error_predicated": no_spare_error_predicated,
            "optimized_capacity": optimized_capacity,
        },
        True,
        False,
    )

    show_html(html_template, "plan-editor")
