import csv
import datetime
import os
import subprocess
import sys

import click

from hcs_cli.cmds.dev.fs.helper.k8s_util import kubectl


@click.group()
def emqx():
    """Retrieve information from HDC EMQX MQTT."""
    pass


def _format_time(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp) / 1000).strftime("%Y-%m-%d %H:%M:%S")


@emqx.command()
def clients():
    "Show clients"
    clients0 = kubectl("exec -t emqx-0 -- emqx_ctl clients list", show_command=False).stdout
    clients1 = kubectl("exec -t emqx-1 -- emqx_ctl clients list", show_command=False).stdout
    clients2 = kubectl("exec -t emqx-2 -- emqx_ctl clients list", show_command=False).stdout

    clients = clients0 + "\n" + clients1 + "\n" + clients2
    clients = clients.split("\n")
    parsed_clients = []
    for line in clients:
        line = line.strip()
        if not line:
            continue

        # example:
        # Client(CC352FF1204D2B3DCC23840EF9C94097_infra-vsphere-module_image-engine-788bbbdf97-fnbhz, username=CC352FF1204D2B3DCC23840EF9C94097_infra-vsphere-module, peername=100.108.20.231:60879, clean_start=true, keepalive=30, session_expiry_interval=0, subscriptions=2, inflight=0, awaiting_rel=0, delivered_msgs=8, enqueued_msgs=0, dropped_msgs=0, connected=true, created_at=1753807525464, connected_at=1753807525465)

        if line.startswith("Client(") and line.endswith(")"):
            content = line[len("Client(") : -1]
            parts = content.split(", ")
            result = {}
            # The first part is the client id and name, e.g. CC352FF1204D2B3DCC23840EF9C94097_infra-vsphere-module_image-engine-788bbbdf97-fnbhz
            if parts:
                client_info = parts[0]
                if "(" in client_info:
                    client_info = client_info.split("(", 1)[-1]
                result["client"] = client_info
                for part in parts[1:]:
                    if "=" in part:
                        k, v = part.split("=", 1)
                        result[k.strip()] = v.strip()
            parsed_clients.append(result)

    # 'disconnected_at' is a epoch timestamp. convert it to datetime string
    for client in parsed_clients:
        if "disconnected_at" in client:
            client["disconnected_at"] = _format_time(client["disconnected_at"])
        if "created_at" in client:
            client["created_at"] = _format_time(client["created_at"])
        if "connected_at" in client:
            client["connected_at"] = _format_time(client["connected_at"])

    # Collect all unique field names from all parsed_clients
    headers = [
        "client",
        "username",
        "connected",
        "created_at",
        "connected_at",
        "disconnected_at",
        "subscriptions",
        "clean_start",
        "keepalive",
        "session_expiry_interval",
        "peername",
        "awaiting_rel",
        "inflight",
        "delivered_msgs",
        "enqueued_msgs",
        "dropped_msgs",
    ]

    for client in parsed_clients:
        for k in client.keys():
            if k not in headers:
                headers.append(k)

    # write parsed clients to file as csv
    with open("emqx-clients.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(parsed_clients)

    csv_path = os.path.abspath("emqx-clients.csv")
    if sys.platform == "darwin":
        subprocess.run(["open", csv_path])
    elif sys.platform == "win32":
        os.startfile(csv_path)
    else:
        subprocess.run(["xdg-open", csv_path])

    return parsed_clients


@emqx.command()
def routes():
    "Show routes"
    routes0 = kubectl("exec -t emqx-0 -- emqx_ctl routes list", show_command=False).stdout
    routes1 = kubectl("exec -t emqx-1 -- emqx_ctl routes list", show_command=False).stdout
    routes2 = kubectl("exec -t emqx-2 -- emqx_ctl routes list", show_command=False).stdout

    routes = routes0 + "\n" + routes1 + "\n" + routes2
    # routes = routes.split("\n")
    # parsed_routes = []
    # for line in routes:
    #     line = line.strip()
    #     if not line:
    #         continue
    #     parsed_routes.append(line)
    # return parsed_routes
    return routes


@emqx.command()
def subscriptions():
    "Show subscriptions"
    subscriptions0 = kubectl("exec -t emqx-0 -- emqx_ctl subscriptions list", show_command=False).stdout
    subscriptions1 = kubectl("exec -t emqx-1 -- emqx_ctl subscriptions list", show_command=False).stdout
    subscriptions2 = kubectl("exec -t emqx-2 -- emqx_ctl subscriptions list", show_command=False).stdout

    subscriptions = subscriptions0 + "\n" + subscriptions1 + "\n" + subscriptions2
    # subscriptions = subscriptions.split("\n")
    # parsed_subscriptions = []
    # for line in subscriptions:
    #     line = line.strip()
    #     if not line:
    #         continue
    #     parsed_subscriptions.append(line)
    # return parsed_subscriptions
    return subscriptions
