#!/usr/bin/env python3

import os
import ssl
import time


def test_mqtt_pubsub(host, port, ca_certs, cert_file, key_file, resource_id):

    import paho.mqtt.client as mqtt
    from paho.mqtt.client import CallbackAPIVersion, MQTTMessage

    os.environ["PYTHONHTTPSVERIFY"] = "0"
    os.environ["SSL_VERIFY"] = "0"

    print("MQTT host:      " + host)
    print("MQTT port:      " + str(port))
    print("MQTT ca_certs:  " + ca_certs)
    print("MQTT cert_file: " + cert_file)
    print("MQTT key_file:  " + key_file)

    _success = False
    _subscribed = False

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client: mqtt.Client, userdata, connect_flags, reason_code, properties):
        print("on_connect", userdata, connect_flags, reason_code, properties)

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # topic = f"uag/{resource_id}/agent/nanw-demo"
        topic = f"uag/{resource_id}/events"

        # topic_pattern = f"uag/+/agent/nanw-demo"
        topic_pattern = f"uag/{resource_id}/events"
        ret = client.subscribe(topic_pattern)

        print(f"Subscribe returns: {ret}")

        # Send test message in a separate thread
        def publish_message():
            while not _subscribed:
                print("Waiting for subscription to complete...")
                time.sleep(1)
            print("Publishing...")
            ret = client.publish(topic, '{"hello": "mortal"}')
            print(f"Publish returns: {ret}")
            print("Waiting for message...")

        import threading

        thread = threading.Thread(target=publish_message)
        thread.start()

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg: MQTTMessage):
        print(
            f"on_message: topic={msg.topic}, QoS={msg.qos}, timestamp={msg.timestamp}, dup={msg.dup}, retain={msg.retain}, mid={msg.mid}, info={msg.info}, payload={msg.payload}, userdata={userdata}"
        )
        nonlocal _success
        _success = True
        client.disconnect()
        client.loop_stop()

    def on_connect_fail(client, userdata):
        print("on_connect_fail", userdata)

    def on_publish(client, userdata, mid, reason_code, properties):
        print("on_publish", userdata, mid, reason_code, properties)
        if reason_code.is_failure:
            client.disconnect()
            client.loop_stop()

    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        print("on_disconnect", userdata, disconnect_flags, reason_code, properties)
        client.loop_stop()

    def on_subscribe(client, userdata, mid, reason_code_list, properties):
        print("on_subscribe", userdata, mid, reason_code_list, properties)
        r = reason_code_list[0]
        if r.is_failure:
            client.disconnect()
            client.loop_stop()
            return
        nonlocal _subscribed
        _subscribed = True

    def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
        print("on_unsubscribe", userdata, mid, reason_code_list, properties)

    def on_socket_open(client, userdata, socket):
        print("on_socket_open", userdata, socket)

    def on_socket_close(client, userdata, socket):
        print("on_socket_close", userdata, socket)

    client = mqtt.Client(
        client_id=resource_id,
        clean_session=True,
        callback_api_version=CallbackAPIVersion.VERSION2,
        reconnect_on_failure=False,
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_connect_fail = on_connect_fail
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_unsubscribe = on_unsubscribe
    client.on_socket_open = on_socket_open
    client.on_socket_close = on_socket_close

    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.set_ciphers("ALL:@SECLEVEL=0")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        client.tls_set_context(context)
    except Exception:
        client.tls_set(ca_certs=None, certfile=cert_file, keyfile=key_file, cert_reqs=ssl.CERT_NONE)
    client.connect(host, port, 60)
    client.loop_forever()
    if _success:
        print("✅ SUCCESS")
    else:
        print("❌ MQTT test failed")


def _write_file(file_path: str, text: str):
    with open(file_path, "w") as file:
        file.write(text)


def prepare_cert(org_id: str):
    from hcs_core.util import pki_util

    from hcs_cli.service.pki import certificate

    resource_name = "uag10762"
    cert_path = "./"

    os.makedirs(cert_path, exist_ok=True)

    csr_pem, private_key_pem = pki_util.generate_CSR(resource_name, key_length=2048)
    client_cert_chain_pem = certificate.sign_resource_cert_with_org(org_id, csr_pem, 2, "omnissa")
    client_cert_chain_legacy_pem = certificate.sign_resource_cert_with_org(org_id, csr_pem, 2, "legacy")
    client_cert_chain_no_org = certificate.sign_resource_cert_without_org(org_id, csr_pem, 2, "omnissa")

    key_file = cert_path + resource_name + ".key"
    _write_file(key_file, private_key_pem)

    client_cert_chain_file = cert_path + resource_name + ".crt"
    _write_file(client_cert_chain_file, client_cert_chain_pem)

    client_cert_chain_legacy_file = cert_path + resource_name + ".legacy.crt"
    _write_file(client_cert_chain_legacy_file, client_cert_chain_legacy_pem)
    client_cert_chain_no_org_file = cert_path + resource_name + ".noorg.crt"
    _write_file(client_cert_chain_no_org_file, client_cert_chain_no_org)

    root_ca_pem = ""
    for ca_label, ca_pem in certificate.get_all_root_ca().items():
        root_ca_pem += ca_pem
    _write_file(cert_path + "root-ca.pem", root_ca_pem)

    return {
        "key_file": key_file,
        "client_cert_chain_file": client_cert_chain_file,
        "client_cert_chain_legacy_file": client_cert_chain_legacy_file,
        "client_cert_chain_no_org_file": client_cert_chain_no_org_file,
        "root_ca_file": cert_path + "root-ca.pem",
        "resource_name": resource_name,
        "org_id": org_id,
    }


def test_mqtt(host: str, port: int, cert_config: dict, cert_name: str = None):
    if not cert_name:
        cert_name = "client_cert_chain_file"
    cert_file_name = cert_config[cert_name]
    test_mqtt_pubsub(
        host=host,
        port=port,
        ca_certs=cert_config["root_ca_file"],
        cert_file=cert_file_name,
        key_file=cert_config["key_file"],
        resource_id=cert_config["resource_name"],
    )
