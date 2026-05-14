import requests
import urllib3
import paho.mqtt.publish as publish
import time
from datetime import datetime

urllib3.disable_warnings()

#Proxmox server IP and port
PROXMOX = "https://XXX.XXX.XXX.XXX:XXXX"
#Token ID defined on the proxmox server. needs to have PVEAuditor access 
TOKEN_ID = "token"
#Secret for this ID
TOKEN_SECRET = "secret"

#MQTT local host IP
MQTT_HOST = "XXX.XXX.XXX.XXX"

headers = {"Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"}

while True:

    try:

        r = requests.get(f"{PROXMOX}/api2/json/cluster/resources",headers=headers,verify=False)

        data = r.json()["data"]

        total_cpu = 0
        total_mem_used = 0
        total_mem = 0

        online_nodes = 0
        total_nodes = 0

        total_qemu = 0
        total_lxc = 0

        total_storage_used = 0
        total_storage = 0

        # Storage totals per node
        node_storage = {}

        excluded_storages = [
            "BazwellNAS",
            ]


        for item in data:

            # =========================
            # NODES
            # =========================

            if item["type"] == "node":

                total_nodes += 1

                if item["status"] == "online":
                    online_nodes += 1

                total_cpu += item["cpu"]

                total_mem_used += item["mem"]
                total_mem += item["maxmem"]

                node_name = item["node"]
                node_cpu = round(item["cpu"] * 100,1)
                node_mem = round((item["mem"] / item["maxmem"]) * 100,1)

                publish.single(f"homelab/{node_name}/cpu",node_cpu,hostname=MQTT_HOST)
                publish.single(f"homelab/{node_name}/mem",node_mem,hostname=MQTT_HOST)

            # =========================
            # STORAGE
            # =========================

            if item["type"] == "storage":
                storage_name = item.get("storage")

                if storage_name in excluded_storages:
                    continue

                if item.get("disk") is not None:
                    total_storage_used += item["disk"]

                if item.get("maxdisk") is not None:
                    total_storage += item["maxdisk"]

                storage_node = item.get("node")

                if storage_node:

                    # Create node storage entry
                    if storage_node not in node_storage:
                        node_storage[storage_node] = {"used": 0,"total": 0}

                    # Accumulate storage usage
                    if item.get("disk") is not None:
                        node_storage[storage_node]["used"] += item["disk"]

                    if item.get("maxdisk") is not None:
                        node_storage[storage_node]["total"] += item["maxdisk"]

            # =========================
            # QEMU
            # =========================

            if item["type"] == "qemu":
                total_qemu += 1

            # =========================
            # LXC
            # =========================

            if item["type"] == "lxc":
                total_lxc += 1

        # =========================
        # PER-NODE STORAGE MQTT
        # =========================

        for node_name, storage in node_storage.items():
            storage_name = item.get("storage")

            if storage["total"] > 0:
                storage_percent = round((storage["used"] / storage["total"]) * 100,1)
                publish.single(f"homelab/{node_name}/storage",storage_percent,hostname=MQTT_HOST)

        # =========================
        # CLUSTER TOTALS
        # =========================

        cpu_percent = round((total_cpu / total_nodes) * 100,1)
        mem_percent = round((total_mem_used / total_mem) * 100,1)

        storage_percent = round((total_storage_used / total_storage) * 100,1)

        # =========================
        # CLUSTER MQTT
        # =========================

        publish.single("homelab/cluster/cpu",cpu_percent,hostname=MQTT_HOST)
        publish.single("homelab/cluster/mem",mem_percent,hostname=MQTT_HOST)
        publish.single("homelab/cluster/nodes",f"{online_nodes}/{total_nodes}",hostname=MQTT_HOST)
        publish.single("homelab/cluster/qemu",total_qemu,hostname=MQTT_HOST)
        publish.single("homelab/cluster/lxc",total_lxc,hostname=MQTT_HOST)
        publish.single("homelab/cluster/storage",storage_percent,hostname=MQTT_HOST)
        timestamp = datetime.now().strftime("%H:%M:%S")
        publish.single("homelab/cluster/updated",timestamp,hostname=MQTT_HOST)

        #debug printing
        print("")
        print("===== CLUSTER =====")
        print(f"CPU:      {cpu_percent}%")
        print(f"RAM:      {mem_percent}%")
        print(f"STORAGE:  {storage_percent}%")
        print(f"NODES:    {online_nodes}/{total_nodes}")
        print(f"QEMU:     {total_qemu}")
        print(f"LXC:      {total_lxc}")
        print("")

        print("===== NODES =====")

        for node_name, storage in node_storage.items():

            print(f"{node_name}")

            # Optional storage display
            if storage['total'] > 0:
                node_storage_percent = round((storage['used'] / storage['total']) * 100,1)
                print(f"  STORAGE: {node_storage_percent}%")
        print("")
        print("Cluster stats published successfully")

    except Exception as e:

        print(f"Error: {e}")

    time.sleep(5)
