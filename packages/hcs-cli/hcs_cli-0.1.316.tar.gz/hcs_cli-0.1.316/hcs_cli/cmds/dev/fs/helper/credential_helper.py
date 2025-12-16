import base64

from hcs_core.ctxp import profile

from hcs_cli.cmds.dev.fs.helper.k8s_util import kubectl
from hcs_cli.cmds.dev.util import log


def _get_application_properties_from_configmap(configmap_name: str):
    config = kubectl(f"get configmap {configmap_name}", get_json=True, ignore_error=True)
    if not config:
        log.warn(f"ConfigMap {configmap_name} not found.")
        return {}
    app_properties_text = config["data"].get("application.properties")
    if app_properties_text is not None:
        lines = app_properties_text.split("\n")
        app_properties = {}
        for line in lines:
            if "=" in line:
                key, value = line.split("=", 1)
                app_properties[key.strip()] = value.strip()
        return app_properties

    app_properties_yaml = config["data"].get("application.yml")
    if app_properties_yaml is not None:
        import yaml

        app_properties = yaml.safe_load(app_properties_yaml)
        return app_properties
    raise Exception(f"ConfigMap {configmap_name} does not contain 'application.properties' and not 'application.yml.")


def _get_properties_from_secret(secret_name: str):
    secret_config = kubectl(f"get secret {secret_name}", get_json=True, ignore_error=True)
    if not secret_config:
        log.warn(f"Secret {secret_name} not found.")
        return {}
    data = secret_config["data"]
    keys = list(data.keys())
    for k in keys:
        v = data[k]
        if not v:
            continue
        data[k] = base64.b64decode(v).decode("utf-8")
    return data


def _get_service_credentials_from_properties(properties: dict):
    prefix = "spring.security.oauth2.client.registration."
    secrets = {}
    for k, v in properties.items():
        if k.startswith(prefix):
            key = k[len(prefix) :]
            service_name, prop = key.split(".", 1)
            if service_name.endswith("Service"):
                service_name = service_name[:-7]
            secrets.setdefault(service_name, {})[prop] = v
    return secrets


def get_client_credential_from_k8s_and_update_profile():
    profile_data = profile.current()

    # get auth service info
    app_properties = _get_application_properties_from_configmap("common-config")
    auth_service_token_url = app_properties["spring.security.oauth2.client.provider.auth-service.token-uri"]
    profile_data.setdefault("auth", {})["tokenUrl"] = auth_service_token_url

    # get secrets

    # print(json.dumps(secrets, indent=4))
    secrets = _get_service_credentials_from_properties(_get_application_properties_from_configmap("images"))
    secrets2 = _get_service_credentials_from_properties(_get_properties_from_secret("lcm-service-pki-secret"))
    secrets3 = _get_service_credentials_from_properties(_get_application_properties_from_configmap("scm"))
    secrets4 = _get_service_credentials_from_properties(_get_properties_from_secret("vmhub-service-pki-secret"))
    secrets.update(secrets2)
    secrets.update(secrets3)
    secrets.update(secrets4)

    override = profile_data.setdefault("override", {})
    for service_name, props in secrets.items():
        override[service_name] = props

    profile.save()
