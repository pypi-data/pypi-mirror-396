import json
import sys
from datetime import datetime, timezone
from typing import Union

import yumako
from hcs_core.sglib.client_util import hdc_service_client

_client = hdc_service_client("hoc-diagnostic")


# def client(region: str) -> Elasticsearch:
#     global _client
#     c = _client_map.get(region)
#     if not c:
#         hoc_config = profile.current().hoc
#         if not hoc_config:
#             raise CtxpException("Config not found: profile.hoc. Use 'hcs profile edit' to update.")
#         es_config_map = hoc_config.es
#         if not es_config_map:
#             raise CtxpException("Config not found: profile.hoc.es. Use 'hcs profile edit' to update.")
#         if region not in es_config_map:
#             raise CtxpException(f"Config not found: profile.hoc.es.{region}. Use 'hcs profile edit' to update.")
#         es_config = es_config_map[region]
#         if not es_config.url:
#             raise CtxpException("Config not found: profile.hoc.es.url. Use 'hcs profile edit' to update.")
#         if not es_config.username:
#             raise CtxpException("Config not found: profile.hoc.es.username. Use 'hcs profile edit' to update.")
#         if not es_config.password:
#             raise CtxpException("Config not found: profile.hoc.es.password. Use 'hcs profile edit' to update.")

#         c = Elasticsearch(
#             es_config.url,
#             verify_certs=False,
#             http_compress=True,
#             max_retries=2,
#             retry_on_timeout=True,
#             http_auth=(es_config.username, es_config.password),
#         )
#         _client_map[region] = c
#     return c


def query(
    from_date: Union[str, datetime],
    to_date: Union[str, datetime] = "now",
    template_file: str = None,
    template: str = None,
    **kwargs,
):
    if template_file:
        with open(template_file, "r") as f:
            text = f.read()
    elif template:
        text = template
    else:
        raise ValueError("Either template_file or template must be provided")

    replacements = kwargs
    if "from" in replacements:
        raise ValueError("from is a reserved keyword")
    if "to" in replacements:
        raise ValueError("to is a reserved keyword")
    # if "oid" in replacements:
    #     replacements["oid"] = replacements["oid"].replace("-", "\\\\-")

    from_datetime = yumako.time.of(from_date, tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    to_datetime = yumako.time.of(to_date, tz=timezone.utc).replace(hour=23, minute=59, second=59)
    replacements["from"] = int(from_datetime.timestamp() * 1000)
    replacements["to"] = int(to_datetime.timestamp() * 1000)
    text = yumako.template.replace(text, replacements)

    # Split the multi-line text into two JSON objects by finding the boundary
    json_objects = text.split("}\n{")
    if len(json_objects) != 2:
        raise ValueError("Expected two JSON objects in template")

    # Restore the split delimiters
    json_objects[0] = json_objects[0] + "}"
    json_objects[1] = "{" + json_objects[1]

    try:
        payload_type = json.loads(json_objects[0])
        payload_query = json.loads(json_objects[1])
    except Exception as e:
        print(text, file=sys.stderr)
        raise e

    payload_jsonp = json.dumps(payload_type) + "\n" + json.dumps(payload_query) + "\n"
    return raw_query(payload_jsonp)


def raw_query(payload_jsonp: str):
    return _client.post("/v1/data/query/search", text=payload_jsonp)
