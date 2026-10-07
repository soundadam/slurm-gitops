# 硬件清单

由 `tools/survey.sh` 生成，不要手改。采集日期：2026-09-28, 2026-10-07。每台节点只读自己的 `/sys`、`/proc` 与 `nvidia-smi`，不需要 root。

## 汇总

- 节点 20 台，其中带 BMC 的服务器 7 台，其余是台式机主板。
- GPU 76 张，显存合计 1872 GiB：20× RTX 3080 Ti（12G）、16× RTX 3090（24G）、16× RTX 4090（24G）、8× RTX 5880 Ada（48G）、8× RTX 4090（48G）、4× RTX 4070（12G）、4× RTX 3060（12G）。
- CPU 线程合计 1384，内存合计 3591 GiB。
- 本地盘裸容量：HDD 138.0T、SSD 66.5T、NVME 45.9T。
- 各节点 `/data*` 已用 179.8T / 235.8T（76%），其中用量超过 85% 的有 39 / 65 个。
- 每台节点最快的已连接网口：1G × 18 台、10G × 2 台。

## 机器

| 节点 | 厂商 / 型号 | 形态 | CPU | 线程 | 内存 | BMC |
| --- | --- | --- | --- | --- | --- | --- |
| g0 | ASUS | 台式机 | 1× Core i7-13700KF | 24 | 63G | — |
| g1 | ASUS | 台式机 | 1× Core i7-13700F | 24 | 31G | — |
| g2 | 组装机 | 台式机 | 1× Core i7-8700K | 12 | 31G | — |
| g3 | ASUS | 台式机 | 1× Core i7-13700F | 24 | 31G | — |
| g4 | 组装机 | 台式机 | 1× Core i7-8700 | 12 | 31G | — |
| g5 | 组装机 | 台式机 | 1× Core i7-9800X | 16 | 62G | — |
| g6 | Gigabyte Technology Co., Ltd. Z490 UD | 台式机 | 1× Core i7-10700 | 16 | 31G | — |
| g7 | ASUS | 台式机 | 1× Core i7-11700 | 16 | 39G | — |
| g8 | Supermicro SYS-4029GP-TRT | 服务器 | 2× Xeon Gold 6238R | 112 | 220G | 有 |
| g9 | Supermicro SYS-4029GP-TRT-BA001 | 服务器 | 2× Xeon Silver 4114 | 40 | 93G | 有 |
| g10 | ASUS | 台式机 | 1× Core i7-13700F | 24 | 31G | — |
| g11 | ASUS | 台式机 | 1× Core i7-13700KF | 24 | 31G | — |
| g12 | ASUSTeK COMPUTER INC. ESC8000A-E11 | 服务器 | 2× EPYC 7K62 48-Core | 192 | 252G | 有 |
| g13 | ASUSTeK COMPUTER INC. ESC8000A-E11 | 服务器 | 2× EPYC 7K62 48-Core | 192 | 504G | 有 |
| g14 | ASUSTeK COMPUTER INC. ESC8000A-E11 | 服务器 | 2× EPYC 7K62 48-Core | 192 | 504G | 有 |
| g15 | ASUS | 台式机 | 1× Core i7-12700F | 20 | 31G | — |
| g16 | ASUS | 台式机 | 1× Core i7-12700F | 20 | 31G | — |
| g17 | ASUS | 台式机 | 1× Core i7-13700KF | 24 | 63G | — |
| g18 | New H3C Technologies Co., Ltd. H3C UniServer R5300 G6 | 服务器 | 2× Xeon Platinum 8473C | 208 | 1008G | 有 |
| g19 | PUERSAI PGA443-D08L | 服务器 | 2× EPYC 7A23 48-Core | 192 | 504G | 有 |

## GPU

| 节点 | 卡 | 单卡显存 | PCIe | 功耗上限 | 驱动 |
| --- | --- | --- | --- | --- | --- |
| g0 | 2× RTX 3080 Ti | 12G | Gen4 x16 | 245W | 595.91.07 |
| g1 | 2× RTX 3080 Ti | 12G | Gen4 x16 | 250W | 595.71.05 |
| g2 | 2× RTX 3080 Ti | 12G | Gen3 x16 | 250W | 580.178.04 |
| g3 | 2× RTX 3080 Ti | 12G | Gen4 x16 | 250W | 595.91.07 |
| g4 | `nvidia-smi` 报错：Unable to determine the device handle for GPU0000:02:00.0: Unknown Error | | | | |
| g5 | 4× RTX 3080 Ti | 12G | Gen3 x16 | 250W | 550.90.07 |
| g6 | 1× RTX 3090 | 24G | Gen3 x16 | 250W | 580.178.04 |
| g7 | 1× RTX 3080 Ti | 12G | Gen4 x16 | 250W | 595.91.07 |
| g8 | 7× RTX 3080 Ti | 12G | Gen3 x16 | 200W | 565.57.01 |
| g9 | 5× RTX 3090 | 24G | Gen3 x16 | 250W | 595.91.07 |
| g10 | 2× RTX 4070 | 12G | Gen4 x16 | 200W | 560.35.05 |
| g11 | 2× RTX 4070 | 12G | Gen4 x16 | 150W | 595.91.07 |
| g12 | 8× RTX 4090 | 24G | Gen4 x16 | 300W | 580.178.04 |
| g13 | 8× RTX 3090 | 24G | Gen4 x16 | 250W | 535.309.01 |
| g14 | 8× RTX 4090 | 24G | Gen4 x16 | 300W | 550.142 |
| g15 | 2× RTX 3060 | 12G | Gen4 x16 | 150W | 595.91.07 |
| g16 | 2× RTX 3060 | 12G | Gen4 x16 | 150W | 580.178.04 |
| g17 | 2× RTX 3090 | 24G | Gen4 x16 | 250W | 550.163.01 |
| g18 | 8× RTX 5880 Ada | 48G | Gen4 x16 | 285W | 595.91.07 |
| g19 | 8× RTX 4090 | 48G | Gen4 x16 | 350W | 550.90.07 |

## 网络

连接速率是交换机协商出来的，网卡上限是这块网卡本身能跑的速度。

| 节点 | 网口 | 型号 | 状态 | 连接速率 | 网卡上限 |
| --- | --- | --- | --- | --- | --- |
| g0 | eno1 | RTL8125 2.5GbE Controller (rev 05) | up | 1G | 2.5G |
| g1 | eno1 | RTL8125 2.5GbE Controller (rev 05) | up | 1G | 2.5G |
| g2 | eno1 | Ethernet Connection (7) I219-V (rev 10) | up | 1G | 1G |
| g3 | eno1 | RTL8125 2.5GbE Controller (rev 05) | up | 1G | 2.5G |
| g4 | eno1 | Ethernet Connection (7) I219-V (rev 10) | up | 1G | 1G |
| g5 | eno1 | Ethernet Connection (2) I219-LM | up | 1G | 1G |
|  | enp4s0 | I210 Gigabit Network Connection (rev 03) | up | 1G | 1G |
| g6 | enp5s0 | RTL8111/8168/8411 PCI Express Gigabit Ethernet Controller (rev 16) | up | 1G | 1G |
| g7 | enp5s0 | Ethernet Controller I225-V (rev 03) | up | 1G | 2.5G |
| g8 | eno1np0 | Ethernet Connection X722 for 10GBASE-T (rev 09) | up | 1G | 10G |
|  | eno2np1 | Ethernet Connection X722 for 10GBASE-T (rev 09) | up | 10G | 10G |
| g9 | eno1np0 | Ethernet Connection X722 for 10GBASE-T (rev 09) | up | 1G | 10G |
|  | eno2np1 | Ethernet Connection X722 for 10GBASE-T (rev 09) | up | 10G | 10G |
| g10 | eno1 | RTL8125 2.5GbE Controller (rev 05) | up | 1G | 2.5G |
| g11 | eno1 | RTL8125 2.5GbE Controller (rev 05) | up | 1G | 2.5G |
| g12 | ens1f0 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens1f1 | I350 Gigabit Network Connection (rev 01) | up | 1G | 1G |
|  | enxf676a99798f6 |  | unknown | — | ? |
| g13 | ens1f0 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens1f1 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens1f2 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens1f3 | I350 Gigabit Network Connection (rev 01) | up | 1G | 1G |
|  | enx8e9bcd20e93c |  | down | — | ? |
| g14 | ens1f0 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens1f1 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens1f2 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens1f3 | I350 Gigabit Network Connection (rev 01) | up | 1G | 1G |
|  | enx3691d96ae74c |  | down | — | ? |
| g15 | eno1 | RTL8125 2.5GbE Controller (rev 05) | up | 1G | 2.5G |
| g16 | eno1 | RTL8125 2.5GbE Controller (rev 05) | up | 1G | 2.5G |
| g17 | eno1 | RTL8125 2.5GbE Controller (rev 05) | up | 1G | 2.5G |
| g18 | ens4f0 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens4f1 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens4f2 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |
|  | ens4f3 | I350 Gigabit Network Connection (rev 01) | up | 1G | 1G |
| g19 | enp193s0f0 | I350 Gigabit Network Connection (rev 01) | up | 1G | 1G |
|  | enp193s0f1 | I350 Gigabit Network Connection (rev 01) | down | — | 1G |

RDMA 设备：g8（irdma0, irdma1）、g9（irdma0, irdma1）。

## 存储资源

只算各节点本地的 `/data*` 与挂进来的网络文件系统；系统盘 `/` 上的用量在下一节逐台列出。

| 介质 | 盘数 | 已用 / 总量 | 占比 |
| --- | --- | --- | --- |
| NVME | 22 | 30.8T / 34.8T | 88% |
| SSD | 26 | 55.8T / 64.0T | 87% |
| HDD | 17 | 93.3T / 137.0T | 68% |
| 合计 | 65 | 179.8T / 235.8T | 76% |

各节点 `/data*` 按已用量从大到小：

| 节点 | 已用 | 总量 | 剩余 | 占比 |
| --- | --- | --- | --- | --- |
| g18 | 33.0T | 35.5T | 2.4T | 93% |
| g14 | 25.9T | 27.6T | 1.7T | 94% |
| g5 | 19.8T | 24.8T | 5.0T | 80% |
| g13 | 19.1T | 27.8T | 8.7T | 69% |
| g19 | 16.5T | 27.7T | 11.2T | 60% |
| g12 | 10.7T | 23.6T | 12.9T | 45% |
| g8 | 10.6T | 11.7T | 1.1T | 90% |
| g9 | 8.3T | 10.8T | 2.5T | 76% |
| g0 | 7.7T | 8.8T | 1.1T | 87% |
| g4 | 4.6T | 5.4T | 807G | 85% |
| g1 | 4.3T | 5.4T | 1.2T | 79% |
| g2 | 4.1T | 4.9T | 832G | 83% |
| g6 | 3.5T | 5.9T | 2.4T | 59% |
| g10 | 2.7T | 3.0T | 260G | 91% |
| g11 | 2.7T | 3.0T | 265G | 91% |
| g7 | 2.0T | 3.9T | 1.9T | 52% |
| g3 | 1.8T | 3.0T | 1.2T | 59% |
| g15 | 918G | 983G | 65G | 93% |
| g16 | 884G | 983G | 99G | 90% |
| g17 | 766G | 983G | 217G | 78% |

网络文件系统：

- `192.168.50.229:/home/nis` 挂在 `/home/nis`，已用 4.4T / 7.6T（57%），19 台节点挂载。
- `192.168.50.229:/home/nis` 挂在 `/home/nis`，已用 3.9T / 7.6T（51%），1 台节点挂载。

### 机械盘

系列、记录方式和级别按厂商公开的型号资料对照，没有读 SMART，通电时间和坏道要有 root 才能查。

| 节点 | 盘 | 容量 | 型号 | 系列 | 记录方式 | 级别 | 挂在 | 已用 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| g13 | sda | 24.0T | WDC WUH722424ALE6L4 | WD Ultrastar DC HC580 | CMR | 企业级 | `/data/hdd0` | 15.6T / 24.0T |
| g18 | sda | 24.0T | WDC WUH722424ALE6L4 | WD Ultrastar DC HC580 | CMR | 企业级 | `/data/hdd0` | 22.5T / 23.9T |
| g5 | sdb | 16.0T | WUH721816ALE6L4 | WD Ultrastar DC HC550 | CMR | 企业级 | `/data/hdd1` | 12.8T / 15.9T |
| g12 | sdb | 16.0T | WUH721816ALE6L4 | WD Ultrastar DC HC550 | CMR | 企业级 | `/data/hdd0` | 4.0T / 15.9T |
| g14 | sda | 16.0T | WUH721816ALE6L4 | WD Ultrastar DC HC550 | CMR | 企业级 | `/data/hdd0` | 14.8T / 15.9T |
| g19 | sdc | 16.0T | WUH721816ALE6L4 | WD Ultrastar DC HC550 | CMR | 企业级 | `/data/hdd0` | 5.4T / 15.9T |
| g0 | sdc | 4.0T | WDC WD40EZAX-00C8UB0 | WD Blue | SMR | 桌面 | `/data/hdd1` | 3.5T / 4.0T |
| g5 | sdc | 4.0T | WDC_WD42EJRX-89BFNY0 | WD Purple | CMR | 监控 | `/data/hdd2` | 3.1T / 3.9T |
| g1 | sdc | 3.0T | TOSHIBA HDWD130 | Toshiba P300 | CMR | 桌面 | `/data/hdd0` | 2.2T / 3.0T |
| g6 | sda | 3.0T | TOSHIBA HDWD130 | Toshiba P300 | CMR | 桌面 | `/data/hdd0` | 1.3T / 3.0T |
| g0 | sdd | 2.0T | WDC WD20EFRX-68EUZN0 | WD Red | CMR | NAS | `/data/hdd0` | 1.5T / 1.9T |
| g2 | sdb | 2.0T | ST2000DM005-2CW102 | Seagate BarraCuda | 未确认 | 桌面 | `/data/hdd0` | 1.3T / 2.0T |
| g4 | sdb | 2.0T | WDC_WD20EURS-63S48Y0 | WD AV-GP | CMR | 监控 | `/data/hdd0` | 1.7T / 2.0T |
| g7 | sda | 2.0T | WDC WD20EURX-64HYZY0 | WD AV-GP | CMR | 监控 | `/data/hdd0` | 688G / 2.0T |
| g9 | sdb | 2.0T | WDC WD20SPZX-00UA7T0 | WD Blue 2.5 英寸 | SMR | 笔记本 | `/data/hdd1` | 1.8T / 2.0T |
| g9 | sda | 1.0T | WDC WD10EJRX-89BDPY0 | WD Purple | CMR | 监控 | `/data/hdd` | 361G / 984G |
| g17 | sda | 1.0T | WDC WD10EZEX-08WN4A1 | WD Blue | CMR | 桌面 | `/data/ssd0` | 766G / 983G |

## 数据的年龄

由 `tools/survey.sh --ages` 采集，采集日期：2026-09-28。逐个文件读大小和时间，不打开文件，不需要 root。容量是文件实际占的盘，文件数只算普通文件。

- 扫了 17 台，扫到 122.4T、218.1M 个文件，是这些节点 `/data*` 已用量 124.1T 的 99%；没有权限进去的目录 590 个。
- 没扫到：g12, g13, g14；网络文件系统不在内。
- **一年以上没修改过的 59.5T，146.7M 个文件，平均每个 0.41 MB；一年以上没读过的 14.0T。**
- 读取时间按 relatime 记：一天最多更新一次，备份、杀毒这类程序读文件也会刷新它，所以「没读过」只会少算，不会多算。复制文件时没带 `-p`，修改时间就是复制的那一刻。

| 距今 | 按修改时间：容量 | 文件数 | 平均大小 | 按读取时间：容量 |
| --- | --- | --- | --- | --- |
| 不到 90 天 | 11.0T | 13.7M | 0.80 MB | 24.0T |
| 90 天–1 年 | 51.9T | 57.7M | 0.90 MB | 84.4T |
| 1–2 年 | 20.0T | 62.4M | 0.32 MB | 5.5T |
| 2–3 年 | 17.8T | 32.4M | 0.55 MB | 4.8T |
| 3 年以上 | 21.7T | 51.9M | 0.42 MB | 3.6T |
| 合计 | 122.4T | 218.1M | 0.56 MB | 122.4T |

各节点：

| 节点 | 扫到 | 文件数 | 一年以上没修改 | 一年以上没读 | 进不去的目录 |
| --- | --- | --- | --- | --- | --- |
| g18 | 32.9T | 59.8M | 6.8T | 185G | 13 |
| g5 | 19.6T | 21.7M | 16.7T | 3.3T | 9 |
| g19 | 15.9T | 15.9M | 1.3T | 29G | 162 |
| g8 | 10.5T | 33.4M | 6.0T | 19G | 33 |
| g9 | 8.1T | 16.0M | 5.7T | 640G | 15 |
| g0 | 7.6T | 14.1M | 6.2T | 4.3T | 4 |
| g4 | 4.5T | 9.6M | 3.0T | 1G | 6 |
| g1 | 4.3T | 9.2M | 3.4T | 24G | 4 |
| g2 | 4.1T | 8.3M | 2.1T | 380G | 23 |
| g6 | 3.4T | 9.2M | 2.9T | 2.5T | 6 |
| g10 | 2.7T | 4.9M | 1.3T | 529G | 3 |
| g11 | 2.6T | 3.5M | 1.0T | 520G | 5 |
| g7 | 2.0T | 3.7M | 1.2T | 1.1T | 2 |
| g3 | 1.7T | 4.0M | 873G | 4G | 4 |
| g15 | 868G | 1.6M | 568G | 372G | 150 |
| g16 | 842G | 1.5M | 357G | 0G | 150 |
| g17 | 759G | 1.7M | 100G | 49G | 1 |

## 各节点的盘

| 节点 | 盘 | 大于 100G 的文件系统（已用 / 总量） |
| --- | --- | --- |
| g0 | NVME 1.0T ZHITAI Ti600 1TB<br>SSD 2.0T ZHITAI SC001 XT 2000GB<br>SSD 480G SanDisk SSD PLUS 480GB<br>HDD 4.0T WDC WD40EZAX-00C8UB0<br>HDD 2.0T WDC WD20EFRX-68EUZN0 | `/` 29G / 455G（6%）<br>`/data/ssd0` 903G / 983G（92%）<br>`/data/ssd1` 1.8T / 2.0T（91%）<br>`/data/hdd1` 3.5T / 4.0T（88%）<br>`/data/hdd0` 1.5T / 1.9T（79%） |
| g1 | NVME 256G GIGABYTE GP-GSM2NE3256GNTD<br>SSD 2.0T Great Wall GW560 2TB<br>SSD 480G SanDisk SSD PLUS 480GB<br>HDD 3.0T TOSHIBA HDWD130 | `/` 35G / 250G（14%）<br>`/data/ssd1` 1.7T / 2.0T（87%）<br>`/data/ssd0` 313G / 472G（66%）<br>`/data/hdd0` 2.2T / 3.0T（75%） |
| g2 | NVME 256G INTEL SSDPEKKW256G8<br>NVME 1.0T WDS100T3X0C-00SJG0<br>SSD 2.0T GLOWAY STK2TS3-S7<br>HDD 2.0T ST2000DM005-2CW102 | `/data/ssd1` 916G / 984G（93%）<br>`/data/ssd2` 1.9T / 2.0T（95%）<br>`/data/hdd0` 1.3T / 2.0T（67%） |
| g3 | NVME 256G GIGABYTE GP-GSM2NE3256GNTD<br>NVME 1.0T WDS100T3X0C-00SJG0<br>SSD 2.0T Great Wall GW560 2TB | `/` 32G / 250G（13%）<br>`/data/ssd0` 846G / 984G（86%）<br>`/data/ssd1` 922G / 2.0T（46%） |
| g4 | NVME 1.0T ZHITAI Ti600 1TB<br>NVME 256G INTEL SSDPEKKW256G8<br>SSD 2.0T Samsung_SSD_870_EVO_2TB<br>HDD 2.0T WDC_WD20EURS-63S48Y0<br>SSD 480G SanDisk_SSD_PLUS_480GB | `/` 94G / 215G（44%）<br>`/data/ssd2` 830G / 983G（84%）<br>`/data/ssd0` 312G / 472G（66%）<br>`/data/ssd1` 1.8T / 2.0T（89%）<br>`/data/hdd0` 1.7T / 2.0T（86%） |
| g5 | NVME 256G INTEL SSDPEKKW256G8<br>SSD 1.0T Samsung_SSD_860_EVO_1TB<br>HDD 16.0T WUH721816ALE6L4<br>HDD 4.0T WDC_WD42EJRX-89BFNY0<br>SSD 4.1T Fanxiang_FP325T_4TB | `/` 31G / 250G（12%）<br>`/data/ssd0` 772G / 984G（78%）<br>`/data/ssd1` 3.1T / 4.0T（77%）<br>`/data/hdd2` 3.1T / 3.9T（79%）<br>`/data/hdd1` 12.8T / 15.9T（81%） |
| g6 | NVME 256G SAMSUNG MZVLB256HBHQ-00A00<br>NVME 1.0T WD Blue SN570 1TB SSD<br>NVME 1.0T WD Blue SN570 1TB SSD<br>HDD 3.0T TOSHIBA HDWD130<br>SSD 1.0T WDC WDS100T2B0A-00SM50 | `/` 47G / 250G（19%）<br>`/data/ssd1` 928G / 984G（94%）<br>`/data/ssd2` 658G / 984G（67%）<br>`/data/ssd0` 560G / 984G（57%）<br>`/data/hdd0` 1.3T / 3.0T（45%） |
| g7 | NVME 512G SAMSUNG MZVL2512HCJQ-00BL7<br>NVME 1.0T WD Blue SN570 1TB SSD<br>NVME 1.0T WD Blue SN570 1TB SSD<br>HDD 2.0T WDC WD20EURX-64HYZY0 | `/` 38G / 501G（8%）<br>`/data/ssd1` 591G / 984G（60%）<br>`/data/ssd2` 762G / 984G（77%）<br>`/data/hdd0` 688G / 2.0T（35%） |
| g8 | NVME 500G Samsung SSD 980 500GB<br>NVME 1.0T WD Blue SN570 1TB SSD<br>NVME 1.0T WD Blue SN570 1TB SSD<br>SSD 4.0T SD Ultra 3D 4TB<br>SSD 1.9T HP SSD S650 1920GB<br>SSD 2.0T ZHITAI SC001 XT 2000GB<br>SSD 2.0T Samsung SSD 870 EVO 2TB | `/` 268G / 491G（55%）<br>`/data/nvme/ssd1` 695G / 984G（71%）<br>`/data/nvme/ssd2` 876G / 984G（89%）<br>`/data/sata/ssd4` 1.8T / 2.0T（93%）<br>`/data/sata/ssd3` 1.8T / 2.0T（89%）<br>`/data/sata/ssd2` 1.7T / 1.9T（91%）<br>`/data/sata/ssd1` 3.7T / 3.9T（95%） |
| g9 | NVME 1.0T WD Blue SN570 1TB SSD<br>NVME 500G Samsung SSD 980 500GB<br>NVME 1.0T WD Blue SN570 1TB SSD<br>HDD 1.0T WDC WD10EJRX-89BDPY0<br>HDD 2.0T WDC WD20SPZX-00UA7T0<br>SSD 2.0T SanDisk SSD PLUS 2000GB<br>SSD 2.0T Samsung SSD 870 QVO 2TB<br>SSD 2.0T SanDisk SSD PLUS 2000GB | `/` 303G / 491G（62%）<br>`/data/ssd1` 810G / 984G（82%）<br>`/data/ssd2` 911G / 984G（93%）<br>`/data/hdd` 361G / 984G（37%）<br>`/data/ssd3` 1.6T / 2.0T（82%）<br>`/data/ssd5` 1.8T / 2.0T（90%）<br>`/data/ssd4` 1.1T / 2.0T（54%）<br>`/data/hdd1` 1.8T / 2.0T（89%） |
| g10 | NVME 512G ZHITAI TiPlus5000 512GB<br>NVME 1.0T ZHITAI TiPlus5000 1TB<br>SSD 2.0T SanDisk SSD PLUS 2000GB | `/` 41G / 502G（8%）<br>`/data/ssd1` 877G / 1.0T（87%）<br>`/data/ssd0` 1.8T / 2.0T（93%） |
| g11 | NVME 256G INTEL SSDPEKKW256G8<br>NVME 1.0T ZHITAI Ti600 1TB<br>NVME 2.0T ZHITAI Ti600 2TB | `/` 31G / 218G（14%）<br>`/data/ssd0` 859G / 983G（87%）<br>`/data/ssd1` 1.8T / 2.0T（93%） |
| g12 | NVME 3.8T INTEL SSDPF2KX038T1<br>SSD 960G SAMSUNG MZ7L3960HCJR-00B7C<br>HDD 16.0T WUH721816ALE6L4<br>SSD 4.0T CT4000BX500SSD1 | `/` 810G / 879G（92%）<br>`/data/ssd1` 3.4T / 3.8T（89%）<br>`/data/ssd2` 3.4T / 3.9T（86%）<br>`/data/hdd0` 4.0T / 15.9T（25%） |
| g13 | NVME 3.8T INTEL SSDPF2KX038T1<br>NVME 960G INTEL SSDPF2KX960HZ<br>HDD 24.0T WDC WUH722424ALE6L4 | `/` 182G / 943G（19%）<br>`/data/ssd0` 3.4T / 3.8T（91%）<br>`/data/hdd0` 15.6T / 24.0T（65%） |
| g14 | NVME 3.8T VO003840KZYWV<br>NVME 960G INTEL SSDPF2KX960HZ<br>HDD 16.0T WUH721816ALE6L4<br>SSD 4.0T WD Blue SA510 2.5 4TB SSD<br>SSD 4.0T SD Ultra 3D 4TB | `/` 87G / 943G（9%）<br>`/data/ssd1` 3.7T / 3.9T（94%）<br>`/data/ssd2` 3.6T / 3.9T（92%）<br>`/data/hdd0` 14.8T / 15.9T（93%）<br>`/data/ssd0` 3.8T / 3.8T（98%） |
| g15 | NVME 512G SAMSUNG MZVL2512HCJQ-00BL7<br>NVME 1.0T Samsung SSD 980 1TB | `/` 87G / 502G（17%）<br>`/data/ssd0` 918G / 983G（93%） |
| g16 | NVME 512G SAMSUNG MZVL2512HCJQ-00BL7<br>NVME 1.0T Samsung SSD 980 1TB | `/` 160G / 502G（32%）<br>`/data/ssd0` 884G / 983G（90%） |
| g17 | NVME 1.0T ZHITAI Ti600 1TB<br>HDD 1.0T WDC WD10EZEX-08WN4A1 | `/` 42G / 934G（4%）<br>`/data/ssd0` 766G / 983G（78%） |
| g18 | NVME 1.9T UP2A61T9SD004LX<br>NVME 1.9T UP2A61T9SD004LX<br>NVME 3.8T SAMSUNG MZQL23T8HCLS-00B7C<br>HDD 24.0T WDC WUH722424ALE6L4<br>SSD 2.0T ZHITAI SC001 XT 2000GB<br>SSD 4.0T WD Blue SA510 2.5 4TB SSD | `/` 55G / 1.8T（3%）<br>`/data/ssd3` 1.9T / 2.0T（94%）<br>`/data/ssd4` 1.7T / 1.9T（90%）<br>`/data/ssd1` 3.4T / 3.8T（90%）<br>`/data/ssd0` 3.6T / 3.9T（92%）<br>`/data/hdd0` 22.5T / 23.9T（94%） |
| g19 | NVME 960G INTEL SSDPF2KX960HZ<br>SSD 4.0T WD Blue SA510 2.5 4TB SSD<br>SSD 4.0T WD Blue SA510 2.5 4TB SSD<br>HDD 16.0T WUH721816ALE6L4<br>SSD 4.0T SD Ultra 3D 4TB | `/` 213G / 943G（23%）<br>`/data/hdd0` 5.4T / 15.9T（34%）<br>`/data/ssd0` 3.7T / 3.9T（95%）<br>`/data/ssd1` 3.7T / 3.9T（93%）<br>`/data/ssd6` 3.7T / 3.9T（95%） |

## 系统与软件

| 节点 | Ubuntu | 内核 | docker（docker 组人数） | Apptainer | `/dev/ipmi0` |
| --- | --- | --- | --- | --- | --- |
| g0 | 22.04 | 6.8.0-138-generic | — | — | — |
| g1 | 22.04 | 6.8.0-136-generic | — | — | — |
| g2 | 22.04 | 6.8.0-138-generic | — | — | — |
| g3 | 22.04 | 6.8.0-138-generic | — | — | — |
| g4 | 20.04 | 5.15.0-139-generic | — | — | — |
| g5 | 20.04 | 5.15.0-139-generic | 有（0） | — | — |
| g6 | 22.04 | 6.8.0-138-generic | — | — | — |
| g7 | 22.04 | 6.8.0-138-generic | — | — | — |
| g8 | 22.04 | 6.8.0-49-generic | — | — | 有 |
| g9 | 22.04 | 6.8.0-138-generic | — | — | 有 |
| g10 | 22.04 | 6.8.0-136-generic | — | — | — |
| g11 | 22.04 | 6.8.0-138-generic | — | — | — |
| g12 | 22.04 | 6.8.0-138-generic | — | — | 有 |
| g13 | 22.04 | 6.8.0-138-generic | — | — | 有 |
| g14 | 22.04 | 6.8.0-136-generic | 有（1） | — | 有 |
| g15 | 22.04 | 6.8.0-138-generic | — | — | — |
| g16 | 22.04 | 6.8.0-138-generic | — | — | — |
| g17 | 22.04 | 6.8.0-136-generic | — | — | — |
| g18 | 22.04 | 6.8.0-138-generic | — | — | 有 |
| g19 | 22.04 | 6.8.0-136-generic | 有（2） | — | 有 |
