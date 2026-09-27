# 文档索引

| 问题 | 文档 |
| --- | --- |
| 集群现状、网络、存储、身份、控制节点、Slurm、作业流、采购，以及待定问题 | [design.md](design.md) |
| 按预算分几档，每档的拓扑、清单、估价 | [tiers.md](tiers.md) |
| 冷存储怎么配：哪些现有的盘能利旧、池怎么排、RAID 与备份、整机清单 | [storage-node.md](storage-node.md) |
| 现有数据怎么全量冻结、整改、再由成员清理 | [migration.md](migration.md) |
| 每台节点的硬件与存储用量（由 `tools/survey.sh` 生成） | [inventory.md](inventory.md) |
| 全量冻结要多久（由 `tools/survey.sh` 生成） | [freeze-estimate.md](freeze-estimate.md) |
| 做到哪了、还缺什么 | [rollout.md](rollout.md) |

design、tiers、storage-node、migration 是工作中的设计，写现状、方案和倾向；inventory 和 freeze-estimate
是采集快照，带采集日期；rollout 是动作清单。
