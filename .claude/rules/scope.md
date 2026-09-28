# 这个仓库是什么

aalab GPU 集群的设计：网络、存储、身份、控制节点与 Slurm 调度，以及它们的上线记录。
集群是实验室共享的，节点上跑着别人的进程。

**在 aalab 节点上动 root 之前先问用户。** 装包、改 PAM、重启守护进程都会影响别的成员，
而 sudo 是用户以具体理由单独申请来的，一次批准不延续到下一件事。
**为什么**：集群不是用户的；搞坏 sshd 或 PAM 会把全实验室锁在门外。

**不在节点之间做内网探测。** 看不到的设备（NIS/NFS 服务器、网关）问用户或管理员，
不从节点上往内网扫端口或多跳 SSH。

**设计还在讨论，不写 ADR。** 方案、倾向和待定问题都在 `docs/` 里，哪层放什么见 [docs.md](docs.md)；
结论没定之前不要把它固化成决定记录，也不要在别处把倾向写成定论。

一个事实只写一处：节点硬件在 `inventory/nodes/*.json`、数据的年龄在 `inventory/ages/*.json`（[inventory.md](../../docs/ref/inventory.md) 与
[freeze-estimate.md](../../docs/ref/freeze-estimate.md) 由它们生成，不手改；估算用的速率假设在 `tools/freeze_estimate.py`），QOS 与分区的数在
[design](../../docs/work/design.md)，还没做的在 [rollout](../../docs/work/rollout.md)。
