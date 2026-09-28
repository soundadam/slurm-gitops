# 文档索引

文档分两层。`ref/` 是写给采购讨论的同事的，整个目录同步到飞书；`work/` 是我们自己的，不出仓库。
哪句话该放哪一层，见 [.claude/rules/docs.md](../.claude/rules/docs.md)。

## ref/：实测的事实、已定的方案和列明的选项

| 问题 | 文档 |
| --- | --- |
| 飞书首页：现状、要解决什么、目标拓扑、先看哪几点 | [README.md](ref/README.md) |
| 现在的网络、管理机、身份、家目录、数据与用法 | [current.md](ref/current.md) |
| 目标架构、数据放在哪、热存储给成员带来的变化 | [plan.md](ref/plan.md) |
| 采购需求单：逐项规格、数量、全新与现货价格 | [purchase.md](ref/purchase.md) |
| 热存储怎么配 | [hot-storage.md](ref/hot-storage.md) |
| 冷存储怎么配：哪些现有的盘能利旧、池怎么排、RAID 与备份、整机清单 | [cold-storage.md](ref/cold-storage.md) |
| 身份服务与控制节点 | [control-and-identity.md](ref/control-and-identity.md) |
| 整改步骤、停机时间、各处资源搬到哪 | [software.md](ref/software.md) |
| 每台节点的硬件与存储用量（由 `tools/survey.sh` 生成） | [inventory.md](ref/inventory.md) |
| 全量冻结要多久（由 `tools/survey.sh` 生成） | [freeze-estimate.md](ref/freeze-estimate.md) |

## work/：倾向、待定问题和动作清单

| 问题 | 文档 |
| --- | --- |
| 网络、存储、身份、控制节点的倾向，Slurm 与作业流，不上飞书的采购考虑，以及待定问题 | [design.md](work/design.md) |
| 现有数据怎么全量冻结、整改、再由成员清理 | [migration.md](work/migration.md) |
| 做到哪了、还缺什么 | [rollout.md](work/rollout.md) |
