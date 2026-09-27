# 这个仓库是什么

aalab GPU 集群的 Slurm 调度方案。集群是实验室共享的，节点上跑着别人的进程，
用户账户来自实验室的 NIS——这些都不归本仓管，本仓只管 Slurm 那一层。

**在 aalab 节点上动 root 之前先问用户。** 装包、改 PAM、重启守护进程都会影响别的成员，
而 sudo 是用户以具体理由单独申请来的，一次批准不延续到下一件事。
**为什么**：集群不是用户的；搞坏 sshd 或 PAM 会把全实验室锁在门外。

**不在节点之间做内网探测。** 看不到的设备（NIS/NFS 服务器、网关）问用户或管理员，
不从节点上往内网扫端口或多跳 SSH。

`114.212.224.242` 是 NAT 出口，只有端口转发，不是能装服务的主机。
控制器放在哪、为什么，在 [ADR-0001](../../docs/adr/0001-controller-inside-aalab-lan.md)。

一个事实只写一处：节点硬件在 [inventory](../../docs/inventory.md)，QOS 与分区的数在
[design](../../docs/design.md)，还没做的在 [rollout](../../docs/rollout.md)。
