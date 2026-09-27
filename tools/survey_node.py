"""Read one node's hardware without root and print it as JSON.

Runs on the node itself (python3 >= 3.8, stdlib only): `ssh aalab.gN python3 - < survey_node.py`.
Hardware and installed software only: no utilisation, no user names.
Reads only the node's own /sys, /proc and user-level tools; never touches the network.
"""

import datetime
import json
import os
import re
import shutil
import socket
import subprocess


def run(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return None


def cpu():
    info = {}
    for line in run("lscpu").splitlines():
        k, _, v = line.partition(":")
        info[k.strip()] = v.strip()
    return {
        "model": info.get("Model name"),
        "sockets": int(info.get("Socket(s)", 0) or 0),
        "cores_per_socket": int(info.get("Core(s) per socket", 0) or 0),
        "threads": os.cpu_count(),
    }


def memory_gib():
    m = re.search(r"MemTotal:\s+(\d+) kB", read("/proc/meminfo") or "")
    return round(int(m.group(1)) / 2**20, 1) if m else None


def gpus():
    fields = "index,name,memory.total,pci.bus_id,pcie.link.gen.max,pcie.link.width.max,power.limit"
    out = run("nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits")
    rows = []
    for line in out.splitlines():
        p = [x.strip() for x in line.split(",")]
        if len(p) != 7 or not p[0].isdigit():
            continue
        rows.append({
            "index": int(p[0]), "name": p[1], "vram_mib": p[2], "bus": p[3],
            "pcie_gen": p[4], "pcie_width": p[5], "power_w": p[6],
        })
    return {
        "driver": (run("nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader").splitlines() or [None])[0],
        "error": None if rows else (run("nvidia-smi").strip().splitlines() or ["nvidia-smi missing"])[0],
        "cards": rows,
    }


def nics():
    out = []
    for n in sorted(os.listdir("/sys/class/net")):
        base = f"/sys/class/net/{n}"
        if not os.path.exists(f"{base}/device"):
            continue  # virtual
        dev = os.path.basename(os.path.realpath(f"{base}/device"))
        desc = run("lspci", "-s", dev).split(": ", 1)[-1].strip()
        speed = read(f"{base}/speed")
        out.append({
            "name": n, "pci": dev, "model": desc, "state": read(f"{base}/operstate"),
            "speed_mbps": int(speed) if speed and speed.lstrip("-").isdigit() and int(speed) > 0 else None,
        })
    return out


def disks():
    data = json.loads(run("lsblk", "-J", "-b", "-o", "NAME,SIZE,TYPE,ROTA,TRAN,MODEL,MOUNTPOINT") or '{"blockdevices": []}')
    out = []
    for d in data["blockdevices"]:
        if d["type"] != "disk" or d["name"].startswith(("loop", "zram")):
            continue
        mounts = []
        def walk(x):
            if x.get("mountpoint"):
                mounts.append(x["mountpoint"])
            for c in x.get("children", []) or []:
                walk(c)
        walk(d)
        kind = "nvme" if d["name"].startswith("nvme") else ("hdd" if str(d["rota"]) in ("1", "True", "true") else "ssd")
        out.append({"name": d["name"], "kind": kind, "tran": d.get("tran"), "model": (d.get("model") or "").strip(),
                    "size_gb": round(int(d["size"]) / 1e9), "mounts": mounts})
    return out


def filesystems():
    out = []
    for line in run("df", "-P", "-B1", "-x", "tmpfs", "-x", "devtmpfs", "-x", "overlay", "-x", "squashfs").splitlines()[1:]:
        p = line.split()
        if len(p) >= 6 and int(p[1]) > 100e9:
            out.append({"source": p[0], "mount": p[5], "size_gb": round(int(p[1]) / 1e9), "used_gb": round(int(p[2]) / 1e9)})
    return out


def pci_summary():
    lines = run("lspci").splitlines()
    return {
        "bmc": [l.split(": ", 1)[-1] for l in lines if re.search(r"ASPEED|BMC|Matrox G200e", l, re.I)],
        "physical_slots": len(os.listdir("/sys/bus/pci/slots")) if os.path.isdir("/sys/bus/pci/slots") else None,
        "infiniband": sorted(os.listdir("/sys/class/infiniband")) if os.path.isdir("/sys/class/infiniband") else [],
    }


def dmi():
    keys = ("sys_vendor", "product_name", "board_vendor", "board_name", "chassis_type", "bios_version")
    return {k: read(f"/sys/class/dmi/id/{k}") for k in keys}


def software():
    os_release = dict(l.split("=", 1) for l in (read("/etc/os-release") or "").splitlines() if "=" in l)
    docker_group = [l for l in (run("getent", "group", "docker")).splitlines()]
    return {
        "os": os_release.get("VERSION_ID", "").strip('"'),
        "kernel": os.uname().release,
        "docker": bool(shutil.which("docker")),
        "docker_group_size": len([u for u in docker_group[0].split(":")[-1].split(",") if u]) if docker_group else 0,
        "apptainer": bool(shutil.which("apptainer") or shutil.which("singularity")),
        "ipmi_dev": os.path.exists("/dev/ipmi0"),
    }


print(json.dumps({
    "host": socket.gethostname(), "surveyed": datetime.date.today().isoformat(), "dmi": dmi(), "cpu": cpu(), "memory_gib": memory_gib(),
    "gpu": gpus(), "nics": nics(), "disks": disks(), "filesystems": filesystems(),
    "pci": pci_summary(), "software": software(),
}, ensure_ascii=False))
