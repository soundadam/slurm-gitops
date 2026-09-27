# ADR-0002 身份用 NIS，权限在 slurmdbd，登录用 pam_slurm_adopt 收口

## 决定

**D1** Slurm 不另建用户。身份沿用实验室现有的 NIS，uid 在所有节点上一致。

**D2** 谁能提交作业、能用多少资源，由 slurmdbd 的关联（account/user/QOS）决定，
并开启 `AccountingStorageEnforce=associations,limits,qos,safe`。关联的内容在本仓用声明式文件描述，差异通过 `sacctmgr` 应用上去。

**D3** 接入 Slurm 的计算节点用 pam_slurm_adopt 限制 SSH 登录，并用 cgroup 限制设备。

**D4** 调度管理用 Slurm 自己的 AdminLevel 和 coordinator 分级，不用 sudo。

## 理由

- 再建一套用户体系就要做同步，uid 一旦不一致，作业就会以别人的身份运行
  （elon 上的 uid 1000 在 aalab 上就是 `nca`）。
- 不开 enforce 的话，限额和 QOS 只是摆设：谁都能用任意 account 提交。
- 不管住 SSH，Slurm 只是一份建议。只要有人能绕过调度直接在节点上跑，
  排队分到这张卡的作业仍然可能撞上别人的进程，「这张卡是我的」这件事就不成立。
- 把权限写进仓、改动走 PR，谁在什么时候给了谁什么权限，都留在 git 历史里。

## 前提

实验室继续用 NIS，或者换成另一套能保证 uid 全局一致的目录服务。
