# 上线清单

待定问题在 [design.md 第 10 节](design.md#10-待定问题)。基础设施和数据冻结在前，对外的步骤和停机时间见
[software](../ref/software.md)；Slurm 的几个阶段排在它们之后灰度接入，为什么分阶段见 design 第 7 节末尾。

## 基础设施

- [ ] 和管理员过一遍 [ref/README](../ref/README.md)，定下 design 第 10 节里的待定问题
- [ ] 第一批下单：核心交换机、2.5G 接入交换机、网卡、冷存储、UPS
- [ ] 第二批下单：热存储准系统、内存、U.2（下单前再询价）
- [ ] 数据网 IP 与 VLAN 规划；逐台换网络
- [ ] 冷存储、热存储建池，NFS 导出，所有节点 autofs 挂 `/project`、`/cold`
- [ ] 家目录从 `nis.nca` 搬到热存储，各节点 `/etc/fstab` 改服务器地址，路径不变
- [ ] 建组清单：每个成员属于哪个组
- [ ] 重装 `nis-slave0` 上身份服务、时钟同步和监控告警，逐台节点切 SSSD；观察一周后停 NIS，重装 `nis.nca` 做第二份副本

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

- [ ] g0–g3、g5–g7、g10–g17 逐台接入
- [ ] g4 修好 GPU 后接入

## 数据冻结

路线和每一步的理由见 [migration.md](migration.md)；需要[方案](../ref/plan.md)里的冷存储和网络到位。

- [ ] 公告冻结日期、冻结范围和冷存储上的保留期限，开两周清理窗口
- [ ] 冷存储建好 ZFS 池，每台节点一个 dataset，外加 home 一个
- [ ] 利旧起步时：第一批冻结 g18、g5、g19 的大盘，校验通过后把 g18 的盘并进主池，g5、g19 的盘改作离线备份盘（[migration「分批冻结」](migration.md#分批冻结)）
- [ ] 管理员在各节点以 root 跑第一遍 rsync，g18 的 24T 机械盘先开
- [ ] 冻结日：停作业、`/data*` 挂只读、第二遍 rsync、核对文件数与字节数、打 `@freeze` 快照
- [ ] 宽限期里跑完逐文件校验
- [ ] 用 `zfs userspace` 给每人出一张清单，跑一次重复文件报告
- [ ] 不可再生的数据有第二份
- [ ] 擦盘改作 `/scratch`，删 `@freeze` 快照
