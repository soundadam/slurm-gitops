"""Bucket the bytes and files under one node's /data* by how long ago they were modified and read.

Runs on the node itself (python3 >= 3.8, stdlib only), at idle IO priority:
`ssh aalab.gN 'ionice -c3 nice -n19 python3 -' < survey_ages.py`.
Stats every file without opening it, so it needs no root and leaves atime alone; a node with tens of
millions of files takes up to an hour or two. Directories it cannot enter are counted, not read.
"""

import datetime
import glob
import json
import os
import socket
import time

# Bucket edges in days. 365 is the line the cold-storage sizing reads: data not modified for a year.
EDGES_DAYS = [90, 365, 730, 1095]


def bucket(age_s):
    return next((i for i, e in enumerate(EDGES_DAYS) if age_s < e * 86400), len(EDGES_DAYS))


def scan(mount, now):
    n = len(EDGES_DAYS) + 1
    r = {"files": 0, "bytes": 0, "denied_dirs": 0,
         "mtime_bytes": [0] * n, "mtime_files": [0] * n, "atime_bytes": [0] * n}
    dev = os.stat(mount).st_dev
    stack = [mount]
    while stack:
        try:
            it = os.scandir(stack.pop())
        except OSError:
            r["denied_dirs"] += 1
            continue
        with it:
            for e in it:
                try:
                    s = e.stat(follow_symlinks=False)
                except OSError:
                    continue
                if e.is_dir(follow_symlinks=False):
                    if s.st_dev == dev:
                        stack.append(e.path)
                elif e.is_file(follow_symlinks=False):
                    size = s.st_blocks * 512  # allocated, which is what a copy has to find room for
                    m = bucket(now - s.st_mtime)
                    r["files"] += 1
                    r["bytes"] += size
                    r["mtime_bytes"][m] += size
                    r["mtime_files"][m] += 1
                    # relatime only moves atime forward once a day and never behind mtime
                    r["atime_bytes"][bucket(now - max(s.st_atime, s.st_mtime))] += size
    return r


now = time.time()
mounts = sorted(m for m in glob.glob("/data*") + glob.glob("/data/*") + glob.glob("/data/*/*") if os.path.ismount(m))
print(json.dumps({
    "host": socket.gethostname(), "surveyed": datetime.date.today().isoformat(), "edges_days": EDGES_DAYS,
    "mounts": {m: scan(m, now) for m in mounts},
}))
