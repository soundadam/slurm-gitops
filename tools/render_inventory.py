"""Render docs/inventory.md from inventory/nodes/*.json (written by tools/survey.sh)."""

import collections
import re

from nodes import data_fs, load, tb

EXPECTED = [f"g{i}" for i in range(20)]

# Fastest speed each NIC model can negotiate; the link speed in the JSON is what the switch gave it.
NIC_MAX = [
    (r"RTL8125|I225|I226", "2.5G"),
    (r"10GBASE-T|X710|X722|X550|82599", "10G"),
    (r"ConnectX-4 Lx|ConnectX-6 Lx|E810-XXV|25G", "25G"),
    (r"ConnectX|E810|100G", "100G"),
    (r"I350|I210|I219|RTL8111|RTL8168", "1G"),
]


def nic_max(model):
    return next((v for pat, v in NIC_MAX if re.search(pat, model)), "?")


def short_gpu(name):
    return name.replace("NVIDIA ", "").replace("GeForce ", "").replace(" Generation", "")


def main():
    nodes = load()
    out = []
    w = out.append
    dates = sorted({d["surveyed"] for d in nodes.values()})
    w("# 硬件清单\n")
    w(f"由 `tools/survey.sh` 生成，不要手改。采集日期：{', '.join(dates)}。"
      "每台节点只读自己的 `/sys`、`/proc` 与 `nvidia-smi`，不需要 root。\n")
    missing = [n for n in EXPECTED if n not in nodes]
    if missing:
        w(f"未采集到：{', '.join(missing)}。\n")

    # totals
    gpus = collections.Counter()
    vram = {}
    for d in nodes.values():
        for c in d["gpu"]["cards"]:
            gpus[short_gpu(c["name"])] += 1
            vram[short_gpu(c["name"])] = round(int(c["vram_mib"]) / 1024)
    disk_kind = collections.Counter()
    for d in nodes.values():
        for k in d["disks"]:
            disk_kind[k["kind"]] += k["size_gb"]
    w("## 汇总\n")
    w(f"- 节点 {len(nodes)} 台，其中带 BMC 的服务器 "
      f"{sum(1 for d in nodes.values() if d['pci']['bmc'])} 台，其余是台式机主板。")
    w(f"- GPU {sum(gpus.values())} 张，显存合计 {sum(vram[k] * v for k, v in gpus.items())} GiB："
      + "、".join(f"{v}× {k}（{vram[k]}G）" for k, v in gpus.most_common()) + "。")
    w(f"- CPU 线程合计 {sum(d['cpu']['threads'] for d in nodes.values())}，"
      f"内存合计 {round(sum(d['memory_gib'] for d in nodes.values()))} GiB。")
    w("- 本地盘裸容量：" + "、".join(f"{k.upper()} {tb(v)}" for k, v in disk_kind.most_common()) + "。")
    local = [f for d in nodes.values() for f in data_fs(d)]
    used, size = sum(f["used_gb"] for f in local), sum(f["size_gb"] for f in local)
    w(f"- 各节点 `/data*` 已用 {tb(used)} / {tb(size)}（{round(100 * used / size)}%），"
      f"其中用量超过 85% 的有 {sum(1 for f in local if f['used_gb'] > 0.85 * f['size_gb'])} / {len(local)} 个。")
    speeds = collections.Counter(
        max((n["speed_mbps"] or 0) for n in d["nics"]) for d in nodes.values())
    w("- 每台节点最快的已连接网口：" + "、".join(
        f"{s // 1000 if s >= 1000 else s}{'G' if s >= 1000 else 'M'} × {c} 台" for s, c in sorted(speeds.items())) + "。\n")

    w("## 机器\n")
    w("| 节点 | 厂商 / 型号 | 形态 | CPU | 线程 | 内存 | BMC |")
    w("| --- | --- | --- | --- | --- | --- | --- |")
    for n, d in nodes.items():
        server = bool(d["pci"]["bmc"])
        model = f"{d['dmi']['sys_vendor']} {d['dmi']['product_name']}".replace("System manufacturer System Product Name", "组装机").replace("System Product Name", "")
        cpu = re.sub(r"\(R\)|\(TM\)|CPU|Processor|@.*|\d+th Gen|Intel|AMD", "", d["cpu"]["model"]).split()
        w(f"| {n} | {model.strip()} | {'服务器' if server else '台式机'} | {d['cpu']['sockets']}× {' '.join(cpu)} "
          f"| {d['cpu']['threads']} | {round(d['memory_gib'])}G | {'有' if server else '—'} |")

    w("\n## GPU\n")
    w("| 节点 | 卡 | 单卡显存 | PCIe | 功耗上限 | 驱动 |")
    w("| --- | --- | --- | --- | --- | --- |")
    for n, d in nodes.items():
        g = d["gpu"]
        if not g["cards"]:
            w(f"| {n} | `nvidia-smi` 报错：{g['error']} | | | | |")
            continue
        c0 = g["cards"][0]
        names = collections.Counter(short_gpu(c["name"]) for c in g["cards"])
        w(f"| {n} | {'、'.join(f'{v}× {k}' for k, v in names.items())} | {round(int(c0['vram_mib']) / 1024)}G "
          f"| Gen{c0['pcie_gen']} x{c0['pcie_width']} | {float(c0['power_w']):.0f}W | {g['driver']} |")

    w("\n## 网络\n")
    w("连接速率是交换机协商出来的，网卡上限是这块网卡本身能跑的速度。\n")
    w("| 节点 | 网口 | 型号 | 状态 | 连接速率 | 网卡上限 |")
    w("| --- | --- | --- | --- | --- | --- |")
    for n, d in nodes.items():
        for i, x in enumerate(d["nics"]):
            model = re.sub(r"^.*?(Corporation|Co\., Ltd\.) ", "", x["model"])
            sp = f"{x['speed_mbps'] // 1000}G" if x["speed_mbps"] else "—"
            w(f"| {n if i == 0 else ''} | {x['name']} | {model} | {x['state']} | {sp} | {nic_max(x['model'])} |")
    w("\nRDMA 设备：" + ("、".join(f"{n}（{', '.join(d['pci']['infiniband'])}）" for n, d in nodes.items() if d["pci"]["infiniband"]) or "无") + "。\n")

    w("## 存储资源\n")
    w("只算各节点本地的 `/data*` 与挂进来的网络文件系统；系统盘 `/` 上的用量在下一节逐台列出。\n")
    fs_all = [(n, f) for n, d in nodes.items() for f in data_fs(d)]
    w("| 介质 | 盘数 | 已用 / 总量 | 占比 |")
    w("| --- | --- | --- | --- |")
    for kind in ("nvme", "ssd", "hdd"):
        fs = [f for _, f in fs_all if f["kind"] == kind]
        u, s = sum(f["used_gb"] for f in fs), sum(f["size_gb"] for f in fs)
        w(f"| {kind.upper()} | {len(fs)} | {tb(u)} / {tb(s)} | {round(100 * u / s)}% |")
    u, s = sum(f["used_gb"] for _, f in fs_all), sum(f["size_gb"] for _, f in fs_all)
    w(f"| 合计 | {len(fs_all)} | {tb(u)} / {tb(s)} | {round(100 * u / s)}% |\n")
    w("各节点 `/data*` 按已用量从大到小：\n")
    w("| 节点 | 已用 | 总量 | 剩余 | 占比 |")
    w("| --- | --- | --- | --- | --- |")
    per = sorted(((n, sum(f["used_gb"] for f in data_fs(d)), sum(f["size_gb"] for f in data_fs(d))) for n, d in nodes.items()),
                 key=lambda t: -t[1])
    for n, u, s in per:
        w(f"| {n} | {tb(u)} | {tb(s)} | {tb(s - u)} | {round(100 * u / s)}% |")
    shared = collections.defaultdict(list)
    for n, d in nodes.items():
        for f in d["filesystems"]:
            if not f["source"].startswith("/dev/"):
                shared[(f["source"], f["mount"], f["used_gb"], f["size_gb"])].append(n)
    w("\n网络文件系统：\n")
    for (src, mnt, u, s), ns in shared.items():
        w(f"- `{src}` 挂在 `{mnt}`，已用 {tb(u)} / {tb(s)}（{round(100 * u / s)}%），{len(ns)} 台节点挂载。")
    w("")

    w("## 各节点的盘\n")
    w("| 节点 | 盘 | 大于 100G 的文件系统（已用 / 总量） |")
    w("| --- | --- | --- |")
    for n, d in nodes.items():
        disks = "<br>".join(f"{k['kind'].upper()} {tb(k['size_gb'])} {k['model']}" for k in sorted(d["disks"], key=lambda k: k["name"]))
        fs = "<br>".join(f"`{f['mount']}` {tb(f['used_gb'])} / {tb(f['size_gb'])}（{round(100 * f['used_gb'] / f['size_gb'])}%）"
                         for f in d["filesystems"] if f["source"].startswith("/dev/"))
        w(f"| {n} | {disks} | {fs} |")

    w("\n## 系统与软件\n")
    w("| 节点 | Ubuntu | 内核 | docker（docker 组人数） | Apptainer | `/dev/ipmi0` |")
    w("| --- | --- | --- | --- | --- | --- |")
    for n, d in nodes.items():
        s = d["software"]
        w(f"| {n} | {s['os']} | {s['kernel']} | {'有（' + str(s['docker_group_size']) + '）' if s['docker'] else '—'} "
          f"| {'有' if s['apptainer'] else '—'} | {'有' if s['ipmi_dev'] else '—'} |")
    print("\n".join(out))


main()
