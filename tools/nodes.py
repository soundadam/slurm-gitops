"""Shared readers for inventory/nodes/*.json."""

import glob
import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")


def load():
    nodes = {}
    for f in glob.glob(os.path.join(ROOT, "inventory/nodes/*.json")):
        nodes[os.path.basename(f)[:-5]] = json.load(open(f))
    return dict(sorted(nodes.items(), key=lambda kv: int(kv[0][1:])))


def tb(gb):
    return f"{gb / 1000:.1f}T" if gb >= 1000 else f"{gb}G"


def data_fs(d):
    """The node's local /data* filesystems, each tagged with the kind of disk under it."""
    kinds = {k["name"]: k["kind"] for k in d["disks"]}
    out = []
    for f in d["filesystems"]:
        if not f["mount"].startswith("/data") or not f["source"].startswith("/dev/"):
            continue
        dev = re.sub(r"(nvme\d+n\d+)p\d+$|(sd[a-z]+)\d+$", lambda m: m.group(1) or m.group(2), f["source"][5:])
        out.append({**f, "kind": kinds.get(dev, "?")})
    return out
