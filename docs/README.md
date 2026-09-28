# 文档索引

文档分两层。`ref/` 是写给采购讨论的同事的，整个目录同步到飞书；`work/` 是我们自己的，不出仓库。
哪句话该放哪一层，见 [.claude/rules/docs.md](../.claude/rules/docs.md)。

## ref/：实测的事实和列明的选项

| 问题 | 文档 |
| --- | --- |
| 飞书首页：这套资料是什么、每篇回答什么 | [README.md](ref/README.md) |
| 按预算分几档，每档的拓扑、清单、估价 | [tiers.md](ref/tiers.md) |
| 冷存储怎么配：哪些现有的盘能利旧、池怎么排、RAID 与备份、整机清单 | [storage-node.md](ref/storage-node.md) |
| 每台节点的硬件与存储用量（由 `tools/survey.sh` 生成） | [inventory.md](ref/inventory.md) |
| 全量冻结要多久（由 `tools/survey.sh` 生成） | [freeze-estimate.md](ref/freeze-estimate.md) |

## work/：倾向、待定问题和动作清单

| 问题 | 文档 |
| --- | --- |
| 集群现状、网络、存储、身份、控制节点、Slurm、作业流、采购倾向，以及待定问题 | [design.md](work/design.md) |
| 现有数据怎么全量冻结、整改、再由成员清理 | [migration.md](work/migration.md) |
| 做到哪了、还缺什么 | [rollout.md](work/rollout.md) |
