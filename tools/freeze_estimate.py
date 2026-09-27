"""Estimate how long a full copy of every node's /data* onto one cold-storage box takes.

Prints docs/freeze-estimate.md. Every node copies all its disks at once; each disk reads at its
media rate, each node is capped by its link, and the cold box is capped by its own ingress.
Bandwidth is shared max-min fairly, so the slowest node sets the total time.
"""

from nodes import data_fs, load, tb

# Sustained large-file rates in MB/s. Directories of many small files copy several times slower,
# so read the results as lower bounds.
DISK_READ = {"hdd": 180, "ssd": 450, "nvme": 1500, "?": 180}
LINK = {1: 112, 2.5: 280, 10: 1100, 25: 2750}
# 16 HDDs as two 8-wide raidz2 vdevs, writing many rsync streams at once.
POOL_WRITE = 1200

def link_now(d):
    return max((x["speed_mbps"] or 0) for x in d["nics"]) / 1000


def link_tier1(n, d):
    """Tier 1 network: every desktop at 2.5G (1G-only boards get a PCIe card), servers at 10G."""
    return 10 if d["pci"]["bmc"] else 2.5


SCENARIOS = [
    ("现网", "冷存储接在现有交换机的 1G 口上，节点不动", lambda n, d: link_now(d), LINK[1]),
    ("冷存储 10G", "冷存储有一个 10G 口，节点的连接不动", lambda n, d: link_now(d), LINK[10]),
    ("档 1 网络", "台式机全部 2.5G（只有千兆口的加一块 2.5G 卡），四台服务器 10G，冷存储 25G", link_tier1, min(LINK[25], POOL_WRITE)),
]


def waterfill(caps, total):
    """Max-min fair split of `total` among demands capped by `caps` (dict key -> cap)."""
    alloc, left, todo = {}, total, dict(caps)
    while todo:
        share = left / len(todo)
        small = {k: c for k, c in todo.items() if c <= share}
        if not small:
            alloc.update({k: share for k in todo})
            return alloc
        for k, c in small.items():
            alloc[k] = c
            left -= c
            del todo[k]
    return alloc


def simulate(nodes, link_of, ingress):
    remaining = {(n, i): f["used_gb"] * 1000 for n, d in nodes.items() for i, f in enumerate(data_fs(d))}
    rate_cap = {(n, i): DISK_READ[f["kind"]] for n, d in nodes.items() for i, f in enumerate(data_fs(d))}
    gbit = {n: link_of(n, d) for n, d in nodes.items()}
    link = {n: LINK[g] for n, g in gbit.items()}
    t, done = 0.0, {}
    while remaining:
        active = {}
        for (n, i) in remaining:
            active.setdefault(n, []).append((n, i))
        node_cap = {n: min(link[n], sum(rate_cap[k] for k in ks)) for n, ks in active.items()}
        node_rate = waterfill(node_cap, ingress)
        rate = {}
        for n, ks in active.items():
            rate.update(waterfill({k: rate_cap[k] for k in ks}, node_rate[n]))
        dt = min(remaining[k] / rate[k] for k in remaining)
        t += dt
        for k in list(remaining):
            remaining[k] -= rate[k] * dt
            if remaining[k] <= 1e-6:
                del remaining[k]
                if not any(k2[0] == k[0] for k2 in remaining):
                    done[k[0]] = t
    return t, done, gbit


def lower_bound(nodes, link_of, ingress):
    """No schedule beats the slowest single disk, the slowest single link, or the ingress."""
    total = sum(f["used_gb"] * 1000 for d in nodes.values() for f in data_fs(d))
    disk = max(f["used_gb"] * 1000 / DISK_READ[f["kind"]] for d in nodes.values() for f in data_fs(d))
    node = max(sum(f["used_gb"] * 1000 for f in data_fs(d)) / LINK[link_of(n, d)] for n, d in nodes.items())
    return max(total / ingress, disk, node)


def hours(s):
    h = s / 3600
    return f"{h / 24:.1f} 天" if h >= 48 else f"{h:.0f} 小时"


def main():
    nodes = load()
    results = [(name, desc, *simulate(nodes, f, cap), lower_bound(nodes, f, cap)) for name, desc, f, cap in SCENARIOS]
    total = sum(f["used_gb"] for d in nodes.values() for f in data_fs(d))
    out = []
    w = out.append
    w("# 全量冻结要多久\n")
    w("由 `tools/freeze_estimate.py` 从 inventory 生成，不要手改。"
      f"把 {len(nodes)} 台节点的 `/data*`（共 {tb(total)}）同时复制到一台冷存储上，"
      "每块盘按介质的顺序读速度读、每台节点受自己的网口限制、冷存储受它的入口限制。"
      "按大文件估算，小文件多的目录会慢好几倍，所以这是下限。第二遍增量同步只传差异，不在这里估算。\n")
    w("「同时开跑」是所有盘一起开始、带宽平分；「最快」是先排最慢的那块盘和那条链路，没有哪种排法能比它快。\n")
    w("| 场景 | 条件 | 同时开跑 | 最快 |")
    w("| --- | --- | --- | --- |")
    for name, desc, t, _, _, lb in results:
        w(f"| {name} | {desc} | {hours(t)} | {hours(lb)} |")
    w("\n各节点复制完的时刻（从同时开始算起）：\n")
    w("| 节点 | 数据量 | " + " | ".join(r[0] for r in results) + " |")
    w("| --- | --- | " + " | ".join("---" for _ in results) + " |")
    order = sorted(nodes, key=lambda n: -results[-1][3][n])
    for n in order:
        used = sum(f["used_gb"] for f in data_fs(nodes[n]))
        cells = [f"{hours(r[3][n])}（{r[4][n]:g}G）" for r in results]
        w(f"| {n} | {tb(used)} | " + " | ".join(cells) + " |")
    w("\n括号里是这个场景下该节点的网口速率。")
    print("\n".join(out))


if __name__ == "__main__":
    main()
