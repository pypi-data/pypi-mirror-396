import base64
import logging
import subprocess
import sys

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import profile
from hcs_core.util import pki_util

import hcs_cli.cmds.dev.util.mqtt_helper as mqtt_helper
import hcs_cli.service.vmhub as vmhub
from hcs_cli.support.exec_util import exec

log = logging.getLogger("mqtt")


@click.group()
def mqtt():
    """MQTT commands for testing and development."""
    pass


@mqtt.command()
@click.option("--full", is_flag=True, default=False, help="Show full info")
def info(full: bool, **kwargs):
    if full:
        exec("kubectl exec -t mqtt-server-0 -- vmq-admin metrics show", inherit_output=True)
        exec("kubectl exec -t mqtt-server-0 -- vmq-admin plugin show", inherit_output=True)
        exec("kubectl exec -t mqtt-server-0 -- vmq-admin listener show", inherit_output=True)
        exec("kubectl exec -t mqtt-server-0 -- vmq-admin cluster show", inherit_output=True)
    exec("kubectl exec -t mqtt-server-0 -- vmq-admin session show", inherit_output=True)


def _is_feature_stack():
    profile_data = profile.current()
    return profile_data.hcs.url.find(".fs.devframe.cp.horizon.omnissa.com") != -1


@mqtt.command()
@cli.org_id
def test(org: str, **kwargs):

    org_id = cli.get_org_id(org)
    print(f"Testing MQTT connection for organization: {org_id}")

    print("Preparing cert via PKI...")
    cert_config = mqtt_helper.prepare_cert(org_id)

    _verify_cert_chain(cert_config["client_cert_chain_file"])
    _verify_cert_chain(cert_config["client_cert_chain_legacy_file"])
    _verify_cert_chain(cert_config["client_cert_chain_no_org_file"])

    profile_data = profile.current()
    for region_config in profile_data.hcs.regions:
        print(f"---- Testing MQTT (cert from PKI) in region: {region_config.name} -----")
        host = region_config.mqtt
        port = 8883 if _is_feature_stack() else 443
        if not host:
            print(f"{region_config.name}: no MQTT host configured")
            continue
        print(f"{region_config.name}: {host}")
        _test_mqtt(host, port, cert_config, "client_cert_chain_file")
        _test_mqtt(host, port, cert_config, "client_cert_chain_legacy_file")
        _test_mqtt(host, port, cert_config, "client_cert_chain_no_org_file")

    test_vmhub_otp(org_id)


def _test_mqtt(host, port, cert_config, cert_name):
    file_name = cert_config[cert_name]
    print("======== CERT: " + file_name + " ========")
    print("---- Testing SSL connection (via openssl) -----")
    cmd = f"openssl s_client -showcerts -connect {host}:{port} -CAfile {cert_config['root_ca_file']} -cert {file_name} -key {cert_config['key_file']}"
    exec(cmd, raise_on_error=False)

    print("---- Testing pub/sub (via mqtt client) -----")
    mqtt_helper.test_mqtt(host, port, cert_config, cert_name=cert_name)


def test_vmhub_otp(org_id: str):
    profile_data = profile.current()
    resource_name = "agent1"
    for region_config in profile_data.hcs.regions:
        print(f"---- Testing MQTT (cert from VMHub) in region: {region_config.name} -----")
        vmhub.credentials.use_region(region_config.name)
        otp = vmhub.credentials.request(org_id, resource_name)
        csr_pem, private_key_pem = pki_util.generate_CSR(resource_name)
        ret = vmhub.credentials.redeem(resource_name, otp, csr_pem, ca_lable="omnissa")
        key_file = f"vmhub_{resource_name}.key"
        cert_file = f"vmhub_{resource_name}.crt"
        ca_file = f"vmhub_{resource_name}.ca"
        with open(key_file, "w") as f:
            f.write(private_key_pem)
        with open(cert_file, "w") as f:
            pem = base64.b64decode(ret.clientCrt).decode("utf-8")
            f.write(pem)
        with open(ca_file, "w") as f:
            pem = base64.b64decode(ret.caCrt).decode("utf-8")
            f.write(pem)

        print("---- Testing SSL connection (via openssl) -----")
        cmd = f"openssl s_client -showcerts -connect {ret.mqttServerHost}:{ret.mqttServerPort} -CAfile {ca_file} -cert {cert_file} -key {key_file}"
        exec(cmd, raise_on_error=False)

        print("---- Testing pub/sub (via mqtt client) -----")
        port = 8883 if _is_feature_stack() else ret.mqttServerPort
        mqtt_helper.test_mqtt_pubsub(
            host=ret.mqttServerHost, port=port, ca_certs=ca_file, cert_file=cert_file, key_file=key_file, resource_id=resource_name
        )


def _verify_cert_chain(cert_chain_file: str):
    print(f"---- Verifying certificate chain: {cert_chain_file} -----")

    # read the cert chain file
    with open(cert_chain_file, "r") as f:
        client_cert_chain = f.read()

    # the cert chain is in PEM format, with leaf at the top, and the reset below.
    # split the chain into two parts: the leaf and the rest
    separator = "-----END CERTIFICATE-----"
    certs = client_cert_chain.split(separator)
    # remove the last empty part if it exists
    if certs[-1].strip() == "":
        certs.pop()
    # add the separator back to each cert
    for i in range(len(certs)):
        certs[i] = certs[i] + separator
    leaf_cert = certs[0]
    rest_certs = certs[1:]
    # write the leaf cert to a temporary file
    with open("leaf_cert.pem", "w") as f:
        f.write(leaf_cert)
    with open("chain.pem", "w") as f:
        f.write("".join(rest_certs))
    indent = "  * "
    for cert in reversed(certs):
        with open("temp.pem", "w") as f:
            f.write(cert)
        # print the CN name of the cert
        cert_info = subprocess.run(
            "openssl x509 -noout -subject -serial -hash -in temp.pem".split(" "),
            capture_output=True,
            text=True,
        )
        # Split output into lines and print each
        stdout = cert_info.stdout.strip()
        subject = ""
        serial = ""
        hash = ""
        for line in stdout.splitlines():
            if line.startswith("subject="):
                subject = line[len("subject=") :]
            elif line.startswith("serial="):
                serial = line[len("serial=") :]
            elif line.strip() and not line.startswith("subject=") and not line.startswith("serial="):
                hash = line.strip()
            else:
                raise ValueError(f"Unexpected line format: {line}")
        print(indent, subject, f"(serial={serial}, hash={hash})")
        indent = "  " + indent

    cmd = "openssl verify -verbose -CAfile chain.pem leaf_cert.pem"
    cp = exec(cmd, raise_on_error=False)
    if cp.returncode != 0:
        print("❌ Certificate verification failed", file=sys.stderr)
    else:
        print("✅ Certificate verification succeeded")
