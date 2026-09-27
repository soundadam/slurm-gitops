# 设计

集群的目标形态：哪些进程在哪、作业怎么排、谁能干什么、成员每天怎么用。
节点硬件见 [inventory.md](inventory.md)；做到哪一步见 [rollout.md](rollout.md)。

## 1. 组件与位置

```
                 114.212.224.242 (NAT，只转发)
                          │
 ┌──────────────── 192.168.50.0/24 ─────────────────────────┐
 │  控制主机 ctl（非 GPU 节点，见 ADR-0001）                  │
 │    slurmctld :6817   slurmdbd :6819   MariaDB（仅本机）   │
 │    StateSaveLocation 在本机磁盘                           │
 │                                                          │
 │  登录节点 login（g2）：sbatch / srun / salloc / sacct       │
 │                                                          │
 │  计算节点 gN：slurmd :6818 + munge + cgroup v2            │
 │                                                          │
 │  已有：NIS + NFS /home/nis（192.168.50.229）             │
 └──────────────────────────────────────────────────────────┘
```

- 控制主机、登录节点和所有计算节点共用一把 munge key，时钟由 chrony 同步。
- configless 模式（`SlurmctldParameters=enable_configless`）：只有控制主机上有
  `slurm.conf`，slurmd 和客户端从 slurmctld 拉取配置。计算节点只需要知道控制器地址。
- 全集群所有节点跑同一个 Slurm 版本。升级顺序是 slurmdbd → slurmctld → slurmd → 客户端。
- 节点上的 Ubuntu 有 20.04、22.04 两种，官方源里的版本都太旧。所以本仓用上游 tarball
  自带的 `debian/` 自己打包，每个 Ubuntu 版本出一套 `.deb`，都带 NVML 插件。

## 2. 分区与 GPU

GPU 用 GRES 声明，`gres.conf` 里写 `AutoDetect=nvml`。型号作为 GRES type，
小写、去掉品牌名：`3080ti`、`3090`、`4070`、`3060`、`4090`、`5880ada`。
显存档位写成节点 Feature：`vram12g`、`vram24g`、`vram48g`。
节点自己的本地数据盘也写成 Feature，比如 `ssd4`，作业需要本地数据时用 `--constraint` 选节点。

| 分区 | 节点 | 用途 | 抢占 |
| --- | --- | --- | --- |
| `gpu`（默认） | 已接入的全部 GPU 节点 | 日常训练 | 不被抢 |
| `debug` | 同上 | 调试、交互 | 不被抢，优先级最高 |
| `scavenge` | 同上 | 用空闲卡跑可中断的作业 | 被 `gpu`、`debug` 和节点主人的作业抢占，抢占后重新排队（REQUEUE） |
| `own-<组>` | 某个组出资购买的节点 | 节点主人专用入口 | 抢占 `scavenge` |

- `SelectType=select/cons_tres`，CPU、内存、GPU 分开记账，一台节点可以同时跑多个作业。
- 每张 GPU 默认配 `DefCpuPerGPU` 个 CPU 线程和 `DefMemPerGPU` 的内存，
  按节点的 CPU、内存与 GPU 之比设。节点之间比例相差很大（g2 是 12 线程配 2 卡，
  g18 是 208 线程配 8 卡），所以这两个值按分区或节点组分别设。
- 抢占用 `PreemptType=preempt/partition_prio`，`PreemptMode=REQUEUE`。
  所以 `scavenge` 里的作业必须能从断点恢复。

Slurm 没法把单独某几张卡（比如 g9 的 0–2 卡）划给某一个人，最小单位是整台节点。
所以卡的归属一律换成节点级别的优先权：主人的作业走 `own-<组>` 分区，
其他人只能以 `scavenge` 的身份用这台节点的空闲卡。

## 3. QOS 与优先级

`PriorityType=priority/multifactor`，按公平份额（fairshare）排队，历史用量的半衰期为 7 天。
一个人或一个组最近用得越多，新作业的排序就越靠后，但不会被拒绝。

| QOS | 适用分区 | 单作业最长 | 每人同时占用 | 备注 |
| --- | --- | --- | --- | --- |
| `normal` | `gpu` | 3 天 | 8 卡 | 默认 |
| `debug` | `debug` | 4 小时 | 1 卡，1 个作业 | 优先级加成 |
| `long` | `gpu` | 14 天 | 2 卡 | 按人授予，不是默认 |
| `scavenge` | `scavenge` | 3 天 | 不限 | 可被抢占 |

上面的数是开跑时的初值，由实验室成员商量后调整，改的时候只改这张表和对应的 `sacctmgr` 声明。

## 4. 权限管理

### 身份：沿用 NIS，Slurm 不另建用户

Slurm 靠 uid 识别用户，作业也以提交者的 uid 在节点上运行。NIS 已经保证同一个人在每台节点上的 uid 相同，
所以新成员进实验室拿到 NIS 账号，就具备了使用 Slurm 的前提。成员离开实验室时，
先在 Slurm 里删掉他的关联，再停 NIS 账号。

### 账户树：slurmdbd 里的关联

```
root
├── <组 A>（一般一位导师或一个课题一个 account）
│   ├── user1
│   └── user2
└── <组 B>
    └── user3
```

- 一个用户只有被加进某个 account 才能提交作业（`AccountingStorageEnforce=associations,limits,qos,safe`）。
- 每个 account 的 fairshare 份额，按实验室约定分配，比如按出资或人数。
- 账户树、各人的 QOS、组的份额在仓里用声明式 YAML 写。一个脚本把 YAML 与
  `sacctmgr show assoc` 的输出对比，只把差异用 `sacctmgr` 应用上去。
  所以谁有什么权限，以本仓 `main` 分支为准，改权限要走 PR。

### 管理角色

| 角色 | 谁 | 能做什么 |
| --- | --- | --- |
| Slurm 管理员（`AdminLevel=Administrator`） | 你和实验室管理员 | 改配置、改账户、操作任何作业 |
| 协管员（`AdminLevel=Operator`） | 每组指定一人 | hold/release、requeue、把节点置为 drain/resume |
| 组协调人（account 的 `coordinator`） | 组负责人 | 在自己组内加人、删人，调组内的限额 |
| 普通成员 | 其他所有人 | 提交、查看、取消**自己的**作业 |

sudo 只给要在节点上装包、改系统文件的人。日常调度管理全都走 `scontrol`/`sacctmgr`，不需要 root。

### 节点上的执行边界

- **cgroup v2**：`ConstrainDevices=yes`、`ConstrainCores=yes`、`ConstrainRAMSpace=yes`。
  作业只能看到分给它的卡，Slurm 会自动设置 `CUDA_VISIBLE_DEVICES`。
- **pam_slurm_adopt**（`PrologFlags=contain`）：计算节点的 sshd 只放行
  在这台节点上有正在运行作业的用户，登进来的会话被收进该作业的 cgroup，
  于是 ssh 进去的会话也只看得到分给作业的卡。管理员组（NIS 组 `slurm-admin`）不受这个限制。
  sshd 的 PAM 栈里要去掉 `pam_systemd`，否则 adopt 会失败。
- **docker 组等同于 root**，属于 docker 组的人可以完全绕开 cgroup。接入 Slurm 的节点上，
  容器改用 Apptainer，docker 组只保留给管理员。
- 节点在 Slurm 里是**整台接入**的：一台节点一旦开了 pam_slurm_adopt，就不再接受绕过调度的直接使用。
  理由见 [ADR-0003](adr/0003-whole-node-phased-rollout.md)。

## 5. 成员的日常作业流

| 场景 | 以前 | 用 Slurm 之后 |
| --- | --- | --- |
| 跑一次训练 | ssh 到某台节点，看 `nvidia-smi` 找空卡，`nohup python ...` | 在 login 上 `sbatch train.sh`，脚本里写 `#SBATCH --gres=gpu:1` |
| 挑卡的型号或显存 | 自己记住哪台节点是什么卡 | `--gres=gpu:4090:2` 或 `--constraint=vram48g` |
| 调参扫描 | 手写循环，自己轮流分卡 | 作业数组：`sbatch --array=0-19%4`，`%4` 表示最多 4 个同时跑 |
| 交互调试 | 直接 ssh 进节点 | `srun -p debug --gres=gpu:1 --pty bash` |
| VS Code / Jupyter | Remote-SSH 直接连节点 | 先 `salloc -p debug --gres=gpu:1 -t 4:00:00`，再 Remote-SSH 连分到的节点；pam_slurm_adopt 会把会话收进这次分配 |
| 数据只在某台节点的本地盘上 | 只能去那台节点跑 | `--constraint=ssd4` 或 `-w g18` |
| 看队列、看用量 | 问群里 | `squeue --me`、`sacct`、`sshare` |

结论：这套作业流适合实验室日常。批量训练、调参扫描和按型号挑卡，都比现在省事。
代价集中在三处：

1. **交互使用要先申请资源。** 习惯直接在节点上开 Jupyter 的人，要多一步 `salloc`。
   `debug` 分区的高优先级就是为了让这一步几乎不用排队。
2. **数据锁在节点本地盘上。** 这类作业只能用 constraint 绑到那台节点，失去自由调度。
   长期看，数据要放到共享存储或对象存储上。
3. **用 docker 的人要改用 Apptainer。**

写给成员的上手文档（一页纸加几个 `sbatch` 模板），在第一台节点接入时一起交付。
