import json
import sys

import click
from hcs_core.ctxp import CtxpException, profile
from hcs_core.sglib.client_util import hdc_service_client, is_regional_service, regional_service_client
from hcs_core.util.query_util import PageRequest


def _has_stdin_data():
    if sys.stdin.isatty():
        return False  # Connected to terminal, no pipe/redirection
    return True  # Stdin is being piped or redirected


def _resolve_data(data_arg):
    """Resolve data from various sources following curl-style conventions."""
    if not data_arg:
        return None

    # Explicit stdin
    if data_arg == "-":
        content = sys.stdin.read()
        return content if content else None

    # File with @ prefix (curl style)
    if data_arg.startswith("@"):
        filepath = data_arg[1:]
        try:
            with open(filepath, "r") as f:
                content = f.read()
            return content if content else None
        except FileNotFoundError:
            raise CtxpException(f"File not found: {filepath}")

    # Raw string
    return data_arg


def _handle_data_input(data_arg, json_arg):
    if data_arg and json_arg:
        raise click.UsageError("Cannot specify both --data and --json options. Use one of them.")

    raw_data = None
    json_data = None

    if data_arg:
        # Explicit --data option provided (raw text)
        if _has_stdin_data() and data_arg != "-":
            raise click.UsageError("Cannot specify --data when data is piped via stdin. Use '--data -' for explicit stdin input.")
        raw_data = _resolve_data(data_arg)
    elif json_arg:
        # Explicit --json option provided (JSON)
        if _has_stdin_data() and json_arg != "-":
            raise click.UsageError("Cannot specify --json when data is piped via stdin. Use '--json -' for explicit stdin input.")
        content = _resolve_data(json_arg)
        if content:
            try:
                json_data = json.loads(content.strip())
            except json.JSONDecodeError as e:
                raise CtxpException(f"Invalid JSON: {e}. File={json_arg}.")
    elif _has_stdin_data():
        # Auto-detect stdin data (treat as json by default)
        stdin_content = sys.stdin.read().strip()
        if stdin_content:
            try:
                json_data = json.loads(stdin_content)
            except json.JSONDecodeError:
                raw_data = stdin_content

    return raw_data, json_data


@click.command()
@click.option("--put", is_flag=True, default=False, help="Perform HTTP PUT.")
@click.option("--post", "-p", is_flag=True, default=False, help="Perform HTTP POST.")
@click.option("--delete", is_flag=True, default=False, help="Perform HTTP DELETE.")
@click.option("--patch", is_flag=True, default=False, help="Perform HTTP PATCH.")
@click.option("--header", "-H", multiple=True, type=str, help="HTTP header to include in the request. Use format 'Header-Name: value'.")
@click.option("--data", "-d", "data_arg", type=str, help="Request data (raw text): string, @file for file, or - for explicit stdin.")
@click.option("--json", "-j", "json_arg", type=str, help="Request data (JSON): JSON string, @file for file, or - for explicit stdin.")
@click.option("--hdc", type=str, required=False, help="HDC name to use. Only valid when the service is a global service.")
@click.option("--region", type=str, required=False, help="Regional name to use. Only valid when the service is a regional service.")
@click.option(
    "--raise-on-404",
    is_flag=True,
    default=False,
    help="Raise an error on HTTP 404 responses. If not set, returns None on 404. Only valid for GET and DELETE methods.",
)
@click.option("--all-pages", is_flag=True, default=False, help="Retrieve all pages of results for paginated GET requests.")
@click.argument("path", type=str, required=True)
def api(
    put: bool,
    post: bool,
    delete: bool,
    patch: bool,
    header: list,
    data_arg: str,
    json_arg: str,
    hdc: str,
    region: str,
    raise_on_404: bool,
    all_pages: bool,
    path: str,
    **kwargs,
):
    """Invoke HCS API by context path."""

    # Determine HTTP method
    method = None
    if put:
        method = "PUT"
    if post:
        if method:
            raise click.UsageError("You cannot specify multiple HTTP method flags.")
        method = "POST"
    if delete:
        if method:
            raise click.UsageError("You cannot specify multiple HTTP method flags.")
        method = "DELETE"
    if patch:
        if method:
            raise click.UsageError("You cannot specify multiple HTTP method flags.")
        method = "PATCH"
    if not method:
        method = "GET"
    if raise_on_404 and method not in ["GET", "DELETE"]:
        raise click.UsageError("The --raise-on-404 option is only applicable for GET and DELETE methods.")

    raw_data, json_data = _handle_data_input(data_arg, json_arg)

    if method in ["GET", "DELETE"] and (raw_data is not None or json_data is not None):
        raise click.UsageError(
            f"Method {method} does not support request body. Use --data or --json or STDIN only with POST, PUT, or PATCH methods."
        )

    if path.startswith(profile.current().hcs.url):
        path = path[len(profile.current().hcs.url) :]
        if not path.startswith("/"):
            path = "/" + path

    if not path.startswith("/"):
        raise click.UsageError("Path must start with a '/'. Please provide a valid context path.")

    service_path = path.split("/")[1]
    api_path = path[len(service_path) + 1 :]
    if is_regional_service(service_path):
        client = regional_service_client(service_path, region=region)
    else:
        client = hdc_service_client(service_path, hdc=hdc)

    if header:
        headers = {h.split(":")[0].strip(): h.split(":")[1].strip() for h in header}
    else:
        headers = None

    # print( f"{method} {api_path} text={raw_data} json={json_data}" )
    if method == "GET":
        if all_pages:

            def _get_page(query_string):
                url = api_path
                if url.find("?") > 0:
                    url += "&" + query_string
                else:
                    url += "?" + query_string
                ret = client.get(url)
                return ret

            response = PageRequest(_get_page, size=100, limit=0).get()
        else:
            response = client.get(api_path, headers=headers, raise_on_404=raise_on_404)
    elif method == "POST":
        response = client.post(api_path, text=raw_data, json=json_data, headers=headers)
    elif method == "PUT":
        response = client.put(api_path, text=raw_data, json=json_data, headers=headers)
    elif method == "DELETE":
        response = client.delete(api_path, headers=headers, raise_on_404=raise_on_404)
    elif method == "PATCH":
        response = client.patch(api_path, text=raw_data, json=json_data, headers=headers)
    else:
        raise click.UsageError(f"Unsupported HTTP method: {method}")
    return response
