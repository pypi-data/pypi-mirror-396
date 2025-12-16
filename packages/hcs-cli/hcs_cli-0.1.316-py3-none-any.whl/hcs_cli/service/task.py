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

from typing import Callable, Dict, List, Optional, Union

from hcs_core.ctxp import recent
from hcs_core.ctxp.util import CtxpException
from hcs_core.sglib.client_util import hdc_service_client, wait_for_res_status
from hcs_core.util.query_util import PageRequest
from pydantic import BaseModel, Field
from yumako import lru

_tsctl_client = hdc_service_client("tsctl")


class LogLevel:
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class RepeatMode:
    NONE = None
    FIXED_RATE = "FixedRate"  # Fixed interval between start of executions
    FIXED_DELAY = "FixedDelay"  # Fixed interval between end and next start


class Schedule(BaseModel):
    initialDelayMs: int = Field(0)
    intervalMs: int = Field(0)
    repeat: Optional[str] = Field(RepeatMode.NONE)
    until: Optional[str] = Field(None)
    timeZone: Optional[str] = Field(None)
    cronExpression: Optional[str] = Field(None)


class LogItem(BaseModel):
    message: str
    time: int
    log_level: Optional[str] = Field(None, alias="logLevel")
    data: Dict = Field(default_factory=dict)


class TaskLog(BaseModel):
    logId: Optional[str] = Field(None)
    group: Optional[str] = None
    taskKey: Optional[str] = Field(None)
    executionId: Optional[str] = Field(None)
    timeStarted: Optional[int] = Field(None)
    timeUpdated: Optional[int] = Field(None)
    timeCompleted: Optional[int] = Field(None)
    timeCreated: Optional[int] = Field(None)
    timeScheduled: Optional[int] = Field(None)
    state: Optional[str] = None
    error: Optional[str] = None
    ttlMs: Optional[int] = Field(None)
    nodeId: Optional[str] = Field(None)
    version: Optional[int] = None
    output: Optional[object] = None
    properties: Optional[Dict] = Field(default_factory=dict)
    logs: List[LogItem] = Field(default_factory=list)


class TaskModel(BaseModel):
    group: str
    key: str
    worker: str
    orgId: Optional[str] = Field(None)
    description: Optional[str] = None
    parent: Optional[str] = None
    resourceId: Optional[str] = Field(None)
    type: Optional[str] = None
    input: Dict = Field(default_factory=dict)
    meta: Dict = Field(default_factory=dict)
    timeCreated: Optional[int] = Field(None)
    exclusive: Optional[str] = None
    exclusiveMode: Optional[str] = Field(None)
    timeoutMs: Optional[int] = Field(None)
    resultTtlMs: Optional[int] = Field(None)
    taskTtlMs: Optional[int] = Field(None)
    lite: Optional[bool] = None
    schedule: Optional[Schedule] = None
    queueId: Optional[str] = Field(None)
    traceContext: Optional[Dict] = Field(None)
    followUp: Optional[object] = Field(None)
    priority: int = 0
    log: Optional[TaskLog] = None
    location: Optional[str] = None


def recent_task(task: TaskModel, namespace: str = None):
    """Set the task as the recent for easy access."""
    recent.set("task.key", task.key)
    recent.set("task.group", task.group)
    if namespace:
        recent.set("task.namespace", namespace)


# This SCM access should be fully removed when global task is supported by tsctl.
_task_temp_lru = lru.LRUDict[str, str]()
_scm_client = hdc_service_client("scm")


def query(namespace: str, fn_filter: Callable = None, **kwargs) -> List[TaskModel]:

    kwargs["size"] = kwargs.get("size", 50)

    def _get_page(query_string):
        url = f"/v1/namespaces/{namespace}/tasks?" + query_string
        return _tsctl_client.get(url)

    ret = PageRequest(_get_page, fn_filter=fn_filter, **kwargs).get()
    return [TaskModel(**item) for item in ret] if ret else []


def _get_v1(namespace: str, group: str, key: str) -> Optional[TaskModel]:
    url = f"/v1/namespaces/{namespace}/groups/{group}/tasks/{key}"
    t = _tsctl_client.get(url, type=TaskModel)
    if not t:
        return
    return t


def _get_v2(org_id: str, namespace: str, group: str, key: str) -> Optional[TaskModel]:
    url = f"/v1/tasks/{key}?"
    if org_id:
        url += f"&orgId={org_id}"
    if namespace:
        url += f"&namespace={namespace}"
    if group:
        url += f"&group={group}"
    t = _scm_client.get(url, type=TaskModel)
    if not t:
        return
    return t


def get(org_id: str, namespace: str, group: str, key: str, **kwargs) -> Optional[TaskModel]:
    _k = f"{namespace}/{group}/{key}"
    version = _task_temp_lru.get(_k)
    if version == "v1":
        t = _get_v1(namespace, group, key)
        t.log = _lastlog(org_id, namespace, group, key)
    elif version == "v2":
        t = _get_v2(org_id, namespace, group, key)
    else:
        t = _get_v1(namespace, group, key)
        if t:
            t.log = _lastlog(org_id, namespace, group, key)
            _task_temp_lru[_k] = "v1"
        else:
            t = _get_v2(org_id, namespace, group, key)
            if t:
                _task_temp_lru[_k] = "v2"

    return t


def delete(org_id: str, namespace: str, group: str, key: str, execution_id: str = None, exclusive_id: str = None, **kwargs):
    url = f"/v1/operation/delete?org_id={org_id}&force=true"
    body = {"namespace": namespace, "group": group, "taskKey": key}

    if execution_id:
        body["executionId"] = execution_id
    else:
        tlog = _lastlog(org_id, namespace, group, key)
        if tlog and tlog.execution_id:
            body["executionId"] = tlog.execution_id

    if exclusive_id:
        body["exclusiveId"] = exclusive_id

    return _tsctl_client.post(url, body)


def cancel(org_id: str, namespace: str, group: str, key: str, **kwargs):
    url = f"/v1/operation/cancel?org_id={org_id}"
    body = {"namespace": namespace, "group": group, "taskKey": key}

    return _tsctl_client.post(url, body)


def retrigger(org_id: str, namespace: str, group: str, key: str, execution_id: str, **kwargs):
    url = f"/v1/operation/retrigger?org_id={org_id}"
    body = {"namespace": namespace, "group": group, "taskKey": key, "executionId": execution_id}

    return _tsctl_client.post(url, body)


def resubmit(org_id: str, namespace: str, group: str, key: str, **kwargs):
    url = f"/v1/operation/resubmit?org_id={org_id}"
    body = {"namespace": namespace, "group": group, "taskKey": key}

    return _tsctl_client.post(url, body)


def logs(org_id: str, namespace: str, group: str, key: str, search: str, **kwargs):
    search_parts = []
    if org_id:
        search_parts.append(f"orgId $eq {org_id}")
    if group:
        search_parts.append(f"group $eq {group}")
    if key:
        search_parts.append(f"taskKey $eq {key}")
    if search:
        search_parts.append(f"({search})")
    final_search = " AND ".join(search_parts)
    kwargs["search"] = final_search

    def _get_page(query_string):
        url = f"/v1/namespaces/{namespace}/tasklog?" + query_string
        return _tsctl_client.get(url)

    return PageRequest(_get_page, **kwargs).get()


def last(org_id: str, namespace: str, group: str, key: str) -> Optional[TaskModel]:
    task = get(org_id, namespace, group, key)
    if not task:
        return
    if task.log:
        return task
    url = f"/v1/namespaces/{namespace}/groups/{group}/tasks/{key}/lastlog"
    task.log = _tsctl_client.get(url)
    return task


def _lastlog(org_id: str, namespace: str, group: str, key: str):
    url = f"/v1/namespaces/{namespace}/groups/{group}/tasks/{key}/lastlog"
    return _tsctl_client.get(url)


def wait(
    org_id: str,
    namespace: str,
    group: str = None,
    key: str = None,
    task: TaskModel = None,
    timeout: str = "1m",
    polling_interval: str = "2s",
    states: Union[str, List[str]] = "Success",
    **kwargs,
):
    if task:
        group = task.group
        key = task.key

    if not namespace:
        raise CtxpException("namespace is required")
    if not group:
        raise CtxpException("group is required")
    if not key:
        raise CtxpException("key is required")

    if isinstance(states, str):
        states = [states]

    terminal_states = ["Success", "Error", "Canceled"]
    transition_states = ["Running", "Init"]
    all_states = terminal_states + transition_states

    # Formalize enum values.
    states = [state[0].upper() + state[1:].lower() for state in states]
    states = ["Canceled" if state == "Cancelled" else state for state in states]

    invalid_states = [state for state in states if state not in all_states]
    if invalid_states:
        raise CtxpException(f"Invalid states: {invalid_states}. Must be one of: {all_states}")

    ready_states = states
    error_states = [state for state in terminal_states if state not in ready_states]
    return wait_for_res_status(
        resource_name=f"{namespace}/{group}/{key}",
        fn_get=lambda: last(org_id=org_id, namespace=namespace, group=group, key=key),
        get_status=lambda t: t.log.state,
        status_map={"ready": ready_states, "error": error_states, "transition": transition_states},
        timeout=timeout,
        polling_interval=polling_interval,
    )


def namespaces():
    return _tsctl_client.get("/v1/namespaces")
