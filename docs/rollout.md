# 上线清单

阶段划分的理由见 [ADR-0003](adr/0003-whole-node-phased-rollout.md)。

## 待定（要问用户或管理员）

- [ ] `192.168.50.229`、`192.168.50.1` 分别是什么设备、谁管，控制主机用哪台（ADR-0001 D2）
- [ ] 登录节点用不用 g2（裸 `ssh aalab` 落在 g2）；它的两张卡进不进 Slurm
- [ ] account 怎么划分（按导师还是按课题），以及各组的份额
- [ ] 哪些节点有明确的主人，需要设 `own-<组>` 分区
- [ ] 各节点上有没有 docker、谁在 docker 组里

## 第 0 阶段：打包

- [ ] 用上游 25.11 tarball 自带的 `debian/` 打出 Ubuntu 22.04 和 20.04 两套 `.deb`，都带 NVML 插件
- [ ] 打包脚本进仓，可以重复构建
- [ ] 部署方式进仓（Ansible：munge、slurmd、slurmctld、slurmdbd、login 各一个 role）
- [ ] 账户声明文件及其差异应用脚本进仓

## 第 1 阶段：elon 控制器 + g18（测试）

已确认：g18 → elon:6817 能连通，elon 的 ufw 已经放行来自 `114.212.224.242` 的 6817。

- [ ] 请管理员在 NAT 上把 `114.212.224.242:6818` 转发到 `192.168.50.28:6818`
- [ ] 在 g18 申请 sudo
- [ ] 在 elon 上建本地用户 `tianchi.liu`，uid 1165（elon 不在 NIS 里，本机的 uid 1000 在 aalab 上是 `nca`）
- [ ] g18 装 munge 和 25.11 的 slurmd，把 elon 的 munge key 拷过去，开启 chrony
- [ ] elon 的测试集群配置：g18 的节点定义里 `NodeAddr=114.212.224.242`，八张卡全部进 GRES
- [ ] 验证：`sbatch` 能跑、`--gres=gpu:N` 只看得到 N 张卡、作业以 uid 1165 运行
- [ ] 验证 slurmdbd、账户关联和 QOS 限额真的会拒绝超额作业
- [ ] 验证 pam_slurm_adopt：没有作业时 ssh 被拒，有作业时会话被收进作业的 cgroup；管理员组可以登录
- [ ] 如果需要在 elon 上用交互式 `srun`：设 `SrunPortRange`，并在 ufw 里给 `114.212.224.242` 放行这段端口

## 第 2 阶段：内网正式控制器 + 大节点试点

- [ ] 控制主机上部署 slurmctld、slurmdbd、MariaDB，开 configless 模式
- [ ] 把 g18 从 elon 迁过来；elon 只保留提交机的身份，或者完全退出
- [ ] 与组负责人商量好后，接入 g19、g8、g9
- [ ] 成员上手文档和 `sbatch` 模板
- [ ] 公告：试点节点开 pam_slurm_adopt 的日期

## 第 3 阶段：其余节点

- [ ] g0–g3、g5–g7、g10、g11、g15–g17 逐台接入
- [ ] g4 修好 GPU 后接入
- [ ] g12–g14 网络连通确认后接入
