import json
import logging

from hcs_core.ctxp import timeutil
from hcs_core.sglib.client_util import hdc_service_client

log = logging.getLogger(__name__)


_client = hdc_service_client("hoc-diagnostic")


def search(payload: dict, size: int = 100):

    pointer_timestamp = timeutil.iso_date_to_timestamp(payload["from"])
    end_timestamp = timeutil.iso_date_to_timestamp(payload["to"])

    count = 0
    while pointer_timestamp < end_timestamp and count < size:

        payload["from"] = timeutil.timestamp_to_iso_date(pointer_timestamp)
        # log.info(f"range: from={payload['from']}, to={payload['to']}")

        page = _client.post("/v1/data/search", json=payload)
        if not page:
            break

        if isinstance(page, str):
            page = json.loads(page)

        if not page:
            break

        # _old = count
        for item in page:

            data = item["data"]

            count += 1
            yield data

            if count >= size:
                break

            pointer_timestamp = max(data["d"]["utcTime"] + 1, pointer_timestamp + 1000)

        # log.info(f"events={count - _old}")
