import json
import re
import sys
from datetime import timezone

import click
import yumako
from hcs_core.sglib import cli_options as cli

from hcs_cli.service import hoc
from hcs_cli.support import predefined_payload


def _formalize_query_string(input_str):
    parts = re.split(r"(?= AND | OR )", input_str)

    for i in range(len(parts)):
        part = parts[i].strip()

        if ":" in part:
            key, value = part.split(":", 1)
            value = value.strip()

            if not (value.startswith('"') and value.endswith('"')):
                value = f'\\"{value}\\"'

            parts[i] = f"{key}:{value}"
        else:
            parts[i] = f'"{part}"'

    return " ".join(parts).strip()


@click.command()
@cli.org_id
@click.option(
    "--from",
    "from_param",
    type=str,
    required=False,
    default="-12h",
    help="Sepcify the from date. E.g. '-1d', or '-1h35m', or '-1w', or '2023-12-04T00:19:22.854Z'.",
)
@click.option(
    "--to",
    type=str,
    required=False,
    default="now",
    help="Sepcify the to date. E.g. 'now', or '-1d', or '-1h35m', or '-1w', or '2023-12-04T00:19:22.854Z'.",
)
@click.option("--service", "-s", type=str, required=True, help="Service name. E.g. inv, lcm")
@click.option("--type", "-t", type=str, required=True, help="Message type. E.g. us:rq:dt, us:rq:vm, us:res:vm")
@click.option(
    "--query",
    "-q",
    type=str,
    required=False,
    help="Additional query. E.g. 'data.d.vid:vm-001 AND data.d.tid:66e05866bc6a4b7401c1419d'",
)
def search(org: str, from_param: str, to: str, service: str, type: str, query: str):
    """Search HOC events for the current org.
    E.g. hcs hoc search -s inv -t us:rq:dt --from -1w -q data.d.s:ns
    """
    org_id = cli.get_org_id(org)

    def _format_time(time: str) -> str:
        dt = yumako.time.of(time, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"

    payload = {
        "from": _format_time(from_param),
        "to": _format_time(to),
        "searchType": "SEARCH_HOC_EVENTS",
        "searchParams": {"search_src": service, "search_type": f'\\"{type}\\"'},
        "searchLocation": "US",
        "additionalFilters": f'AND data.d.oid:\\"{org_id}\\"',
    }

    if query:
        payload["additionalFilters"] += " AND " + _formalize_query_string(query)

    data = hoc.search(payload, 10000)
    return sorted(data, key=lambda item: item["d"]["utcTime"])


@click.command()
@cli.org_id
@click.option(
    "--from",
    "from_param",
    type=str,
    required=False,
    default="-12h",
    help="Sepcify the from date. E.g. '-1d', or '-1h35m', or '-1w', or '2023-12-04T00:19:22.854Z'.",
)
@click.option(
    "--to",
    type=str,
    required=False,
    default="now",
    help="Sepcify the to date. E.g. 'now', or '-1d', or '-1h35m', or '-1w', or '2023-12-04T00:19:22.854Z'.",
)
@click.option(
    "--file",
    "-f",
    type=click.File("rt"),
    default=sys.stdin,
    help="Specify the template file name. If not specified, STDIN will be used.",
)
@click.option("--raw", "-r", is_flag=True, default=False, help="Specify whether the payload is raw jsonp.")
@click.option("--predefined", "-p", type=str, required=False, help="Predefined query name. E.g. 'no_spare'")
def es(org: str, from_param: str, to: str, file, raw: bool, predefined: str):
    """Perform a raw ES query."""
    if predefined:
        text = predefined_payload.load(f"hoc/{predefined}.json.template")
    else:
        with file:
            text = file.read()

    if raw:
        payload_jsonp = text
    else:
        org_id = cli.get_org_id(org)
        payload_type = {
            "search_type": "query_then_fetch",
            "ignore_unavailable": True,
            "index": "hoc-ingested-events*-prod-*",
        }
        text = yumako.template.replace(
            text,
            {
                "from": int(yumako.time.of(from_param, tz=timezone.utc).timestamp() * 1000),
                "to": int(yumako.time.of(to, tz=timezone.utc).timestamp() * 1000),
                "org_id": org_id.replace("-", "\\\\-"),
            },
        )
        try:
            payload_query = json.loads(text)
        except Exception as e:
            print(text, file=sys.stderr)
            print(e, file=sys.stderr)
            return
        payload_jsonp = json.dumps(payload_type) + "\n" + json.dumps(payload_query) + "\n"

    return hoc.es.raw_query(payload_jsonp)
