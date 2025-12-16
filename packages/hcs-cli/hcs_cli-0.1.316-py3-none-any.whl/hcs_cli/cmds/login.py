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

import time

import click
import hcs_core.ctxp as ctxp
import hcs_core.sglib as sglib
from hcs_core.ctxp import recent
from hcs_core.ctxp.util import error_details
from hcs_core.sglib import login_support

from hcs_cli.support import profile as profile_support

# Login use cases:

# 1. Login scenario
# 1.1. As a new user, I want to login.
# 1.2. As a returning user, I want to re-login use the same auth method.
# 1.3. As a returning user, I want to re-login use a different auth method.
# 1.4. As a returning user, I want the system to avoid unnecessary login if the auth is not expired.
# 1.5. As a returning user, I want to re-login with a different org.

# 2. Login type
# 2.1. As a user, I want to login interactively with browser
# 2.2. As a user, I want to login with api-token
# 2.3. As a user, I want to login with refresh-token
# 2.4. As a user, I want to login with client id/secret
# 2.5. As a user, I want to login with csp http basic auth token

# 3. Information
# 3.1. As a user, I want to get the login details (e.g. my permissions)
# 3.2. As a user, I want to get the access token, so I can use it with REST API.


@click.command()
@click.option(
    "--org",
    type=str,
    required=False,
    help="The CSP organization to login. If not specified, the user's default organization will be used.",
)
@click.option("--api-token", type=str, required=False, help="Login with a user CSP API token.")
@click.option("--client-id", type=str, required=False, help="Login with OAuth client ID/secret.")
@click.option("--client-secret", type=str, required=False, help="The OAuth client secret, used with --client-id.")
@click.option("--basic", type=str, required=False, help="Login with a CSP HTTP basic auth token.")
@click.option("--access-token", type=str, required=False, help="Login with a CSP OAuth2 access token.")
@click.option("--refresh-token", type=str, required=False, help="Login with a CSP OAuth2 refresh token.")
@click.option("--browser/--auto", type=bool, default=False, help="Login with browser and remove other configured credentials.")
@click.option(
    "--details",
    "-d",
    default=False,
    is_flag=True,
    help="If specified, return the detailed information about the authentication information, otherwise return only the access token.",
)
@click.option(
    "--refresh",
    "-r",
    default=False,
    is_flag=True,
    help="Used only in non-interactive mode. If specified, forcefully refresh the cached access token.",
)
@click.option(
    "--service",
    "-s",
    required=False,
    help="The service to get login details for, if there's per-service login override.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="If specified, print verbose output.",
)
def login(
    org: str,
    api_token: str,
    client_id: str,
    client_secret: str,
    basic: str,
    access_token: str,
    refresh_token: str,
    browser: bool,
    details: bool,
    refresh: bool,
    service: str,
    verbose: bool,
    **kwargs,
):
    """Login Horizon Cloud Service.

    This command works with the current profile and will update the current profile. If no token is specified, a browser will be launched to login interactively.

    \b
    Examples:
        1. Login with configured credentials, otherwise do an interactive login using browser:
            hcs login
        2. Get login details:
            hcs login -d
        3. Login with CSP org-scope user API token:
            hcs login --api-token <csp-org-scope-user-api-token>
        4. Login with OAuth client id/secret:
            hcs login --client-id <oauth-client-id> --client-secret <oauth-client-secret>
        5. Login with CSP HTTP basic auth token:
            hcs login --basic <csp-http-basic-auth-token>
        6. Login with CSP OAuth2 access token (normally short-lived):
            hcs login --access-token <csp-access-token>
        7. Login with CSP OAuth2 refresh token:
            hcs login --refresh-token <csp-refresh-token>
    """

    current_profile = _ensure_current_profile()

    csp = current_profile.csp

    if service:
        return _get_service_login_override(service, details)
    err = _validate_auth_method(
        org=org, api_token=api_token, client_id=client_id, client_secret=client_secret, basic=basic, browser=browser
    )
    if err:
        return err

    # if org is specified
    if org:
        # update the profile
        csp.orgId = org
        recent.set("org", org)
    else:  # no org id is specified.
        # try using the org_id from profile
        org = csp.orgId

    if api_token:
        _clear_credentials(csp)
        csp.apiToken = api_token
    elif client_id:
        _clear_credentials(csp)
        csp.clientId = client_id
        csp.clientSecret = client_secret
    elif basic:
        _clear_credentials(csp)
        csp.basic = basic
    elif browser:
        _clear_credentials(csp)
    elif access_token:
        oauth_token = {
            "id_token": None,
            "token_type": "bearer",
            "expires_in": 1799,
            "scope": "ALL_PERMISSIONS",
            "access_token": access_token,
            "refresh_token": None,
            "expires_at": time.time() + 1799,
        }
        sglib.auth.save_auth_cache(csp, oauth_token)
    elif refresh_token:
        oauth_token = {
            "id_token": None,
            "token_type": "bearer",
            "expires_in": -1,
            "scope": "ALL_PERMISSIONS",
            "access_token": None,
            "refresh_token": refresh_token,
            "expires_at": time.time() - 1,
        }
        new_token = sglib.auth.refresh_oauth_token(old_oauth_token=oauth_token, csp_url=csp.url)
        sglib.auth.save_auth_cache(csp, new_token)
    else:
        # auto detect mode.
        pass

    interactive = not csp.apiToken and not csp.clientId and not csp.basic and not csp.accessToken and not csp.refreshToken

    # If this is interactive login, it's not ready on production yet. Raise error
    if interactive and not login_support.identify_client_id(csp.url):
        return ctxp.error("The interactive login on the specified stack is not yet available. Try a different authentication method.")

    # If there's existing login info and the org ID is different, logout first
    token = sglib.auth.get_auth_cache(ctxp.profile.current().csp)
    if token:
        ret = sglib.auth.details_from_token(token)
        if csp.orgId and ret["org"].id != csp.orgId:
            if not interactive:
                _echo("Switching to organization " + csp.orgId)
            ctxp.profile.auth.delete()

    err = None
    try:
        oauth_token = sglib.auth.login(force_refresh=refresh, verbose=verbose)
    except Exception as e:
        if interactive:
            oauth_token = _do_browser_login()
        else:
            oauth_token = None
            err = error_details(e)

    if not oauth_token:
        msg = "Login failed."
        if err:
            msg += f" Error: {err}"
        return ctxp.error(msg)
    # else: the token still works

    ctxp.profile.save()

    auth_details = sglib.auth.details(get_org_details=False)
    if csp.orgId:
        if auth_details["org"].id != csp.orgId:
            return ctxp.error(
                f"Org ID ({auth_details['org'].id}) from auth info does not match org ID ({csp.orgId}) in the profile config. This is because the API token is org-scoped and from an org different than the configured org. To fix, either use a new API token matching the specified org, or update the org_id to match the API token. Use 'hcs profile edit' to fix."
            )
    else:
        # org id not specified in profile. Add it.
        csp.orgId = auth_details["org"].id
        ctxp.profile.save()

    return auth_details if details else oauth_token["access_token"]


def _get_service_login_override(service: str, details: bool):
    service_client = sglib.client_util.service_client(service)
    token = service_client._client().token
    if details:
        return sglib.auth.details_from_token(token, False)
    else:
        return token["access_token"]


def _echo(msg):
    click.echo(click.style(msg, fg="yellow"), err=True)


def _do_browser_login():
    auth_config = ctxp.profile.current().csp
    org_id = auth_config.orgId

    _echo("Logging to HCS...")
    _echo(f"  CSP:          {auth_config.url}")
    _echo(f"  Organization: {org_id if org_id else '<default>'}")
    _echo(f"  Profile:      {ctxp.profile.name()}")
    _echo(f"A web browser will be opened at {auth_config.url}. Continue the login in the web browser, and return to this terminal.")
    _echo("If any failure during browser SSO, press CTRL+C to abort and try again, or use other login methods (hcs login --help).")
    token = login_support.login_via_browser(auth_config.url, org_id)
    if token:
        _echo("Success.")
        ctxp.profile.current().csp.browser = True
        if not org_id:
            org_id = sglib.auth.get_org_id_from_token(token)
            _echo(f"Actual org ID: {org_id}")
        sglib.auth.save_auth_cache(auth_config, token)
    return token


def _ensure_current_profile():
    profile = ctxp.profile
    data = profile.current(exit_on_failure=False)
    if not data:
        profile_support.ensure_default_production_profile()
    return profile.current()


def _clear_credentials(csp):
    csp.apiToken = None
    csp.clientId = None
    csp.clientSecret = None


def _validate_auth_method(org: str, api_token: str, client_id: str, client_secret: str, basic: str, browser: bool):
    # validation: API-token and org ID must not be specified together
    if org and api_token:
        return "Invalid arguments. CSP API user token is org-scoped. --org is not needed with --api-token.", 1

    # validation: must not specify duplicated auth methods
    ret = {}
    if api_token:
        ret["api_token"] = 1
    if client_id:
        ret["client_id/secret"] = 1
    if basic:
        ret["basic"] = 1
    if browser:
        ret["browser"] = 1

    if len(ret) > 1:
        return ctxp.error(f"Specify only one authenticate method. Currently specified: {list(ret.keys())}")

    if client_id and not client_secret or not client_id and client_secret:
        return ctxp.error("--client-id and --client-secret must be used in pair.")

    if client_id and not client_secret:
        return ctxp.error("Missing --client-secret, when --client-id is specified.")

    if basic:
        # validate basic token
        client_id, client_secret = sglib.csp._decode_http_basic_auth_token(basic)
