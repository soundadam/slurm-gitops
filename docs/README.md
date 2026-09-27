# 文档索引

| 问题 | 文档 | 类型 |
| --- | --- | --- |
| 集群长什么样、调度怎么划分、权限怎么管、成员怎么用 | [design.md](design.md) | 契约 |
| 控制器为什么放在 aalab 内网 | [ADR-0001](adr/0001-controller-inside-aalab-lan.md) | 理由 |
| 为什么身份用 NIS、权限用 slurmdbd、登录用 pam_slurm_adopt | [ADR-0002](adr/0002-access-model.md) | 理由 |
| 为什么分阶段、按整节点接入 | [ADR-0003](adr/0003-whole-node-phased-rollout.md) | 理由 |
| 节点清单（普查快照） | [inventory.md](inventory.md) | 状态 |
| 做到哪了、还缺什么 | [rollout.md](rollout.md) | 状态 |

契约写目标状态怎么运作；理由写为什么这么定、前提是什么；状态会过期，带日期。
