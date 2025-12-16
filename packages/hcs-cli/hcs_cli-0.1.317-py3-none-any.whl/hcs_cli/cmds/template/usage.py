"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import tempfile
import time
import webbrowser
from datetime import datetime

import click
import hcs_core.sglib.cli_options as cli
import yumako
from hcs_core.ctxp import recent

from hcs_cli.service import scm


def _timestamp_to_date(timestamp: int):
    return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%dT%H:%M")


@click.command(hidden=True)
@click.argument("id", type=str, required=False)
@cli.org_id
def usage(id: str, org: str, **kwargs):
    """Show usage visualization"""

    org_id = cli.get_org_id(org)
    id = recent.require("template", id)

    usage = scm.template_usage(org_id, id)
    if not usage:
        return "No usage data found", 1

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
    html = _get_html(
        id,
        x_axis,
        consumed_capacity,
        spare_capacity,
        no_spare_error,
        consumed_capacity_predicated,
        spare_capacity_predicated,
        no_spare_error_predicated,
        optimized_capacity,
    )

    temp_path = os.path.join(tempfile.gettempdir(), "hcs_template_usage.html")
    with open(temp_path, "w") as f:
        f.write(html)
    try:
        if webbrowser.open("file://" + temp_path, new=0):
            time.sleep(1)
        else:
            return "Failed to open browser", 1
    except Exception as e:
        os.unlink(temp_path)
        return str(e), 1


def _get_html(
    template_name: str,
    x_axis: list,
    consumed_capacity: list,
    spare_capacity: list,
    no_spare_error: list,
    consumed_capacity_predicated: list,
    spare_capacity_predicated: list,
    no_spare_error_predicated: list,
    optimized_capacity: list,
):
    template = """
<html>
<head>
    <script src="https://echarts.apache.org/en/js/vendors/echarts/dist/echarts.min.js"></script>
</head>
<body>
    <div id="main" style="width: 100%;height:400px;"></div>
    <script type="text/javascript">
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option = {
        title: {
            text: "{{template_name}}"
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
            type: 'cross',
            label: {
                backgroundColor: '#6a7985'
            }
            }
        },
        legend: {
            data: [
            'Spare Capacity',
            'Consumed Capacity',
            "No-spare Error",
            'Spare Capacity - Predicated',
            'Consumed Capacity - Predicated',
            "No-spare Error - Predicated",
            'Optimized Capacity'
            ]
        },
        toolbox: {
            feature: {
            saveAsImage: {}
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: {{x_axis}}
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: [
            {
                name: 'Consumed Capacity',
                type: 'line',
                lineStyle: { width: 1 },
                stack: 'Total',
                areaStyle: {},
                emphasis: {
                    focus: 'series'
                },
                color: '#0a0',
                data: {{consumed_capacity}}
            },
            {
                name: 'Spare Capacity',
                type: 'line',
                lineStyle: { width: 1 },
                stack: 'Total',
                label: {
                    show: true
                },
                areaStyle: {},
                emphasis: {
                    focus: 'series'
                },
                color: '#aa0',
                data: {{spare_capacity}},
            },
            {
                name: 'No-spare Error',
                type: 'bar',
                label: {
                    show: true
                },
                areaStyle: {},
                emphasis: {
                    focus: 'series'
                },
                color: '#a00',
                data: {{no_spare_error}},
            },
            {
                name: 'Consumed Capacity - Predicated',
                type: 'line',
                lineStyle: { width: 1 },
                stack: 'Predicated',
                areaStyle: {},
                emphasis: {
                    focus: 'series'
                },
                color: '#6d6',
                data: {{consumed_capacity_predicated}},
            },
            {
                name: 'Spare Capacity - Predicated',
                type: 'line',
                lineStyle: { width: 1 },
                stack: 'Predicated',
                label: {
                    show: true,
                    position: 'top'
                },
                areaStyle: {},
                emphasis: {
                    focus: 'series'
                },
                color: '#dd6',
                data: {{spare_capacity_predicated}},
            },
            {
                name: 'No-spare Error - Predicated',
                type: 'bar',
                label: {
                    show: true
                },
                areaStyle: {},
                emphasis: {
                    focus: 'series'
                },
                color: '#d66',
                data: {{no_spare_error_predicated}},
            },
            {
                name: 'Optimized Capacity',
                type: 'line',
                lineStyle: { width: 1 },
                //areaStyle: {},
                emphasis: {
                    focus: 'series'
                },
                color: '#6dd',
                data: {{optimized_capacity}},
            }
        ]
        };

        option && myChart.setOption(option);
    </script>
</body>
</html>
"""

    return yumako.template.replace(
        template,
        {
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
    )
