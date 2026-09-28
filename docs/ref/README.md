# aalab 集群：硬件与采购参考

aalab GPU 集群采购讨论用的事实和选项：现有的机器实测是什么样，可以怎么买，各要多少钱，买完能解决什么、还剩什么问题。

| 想知道 | 看 |
| --- | --- |
| 按预算分几档，每档买什么、多少钱、解决什么、不解决什么 | [tiers](tiers.md) |
| 冷存储怎么配：现有的盘能利旧多少、池怎么排、整机清单和估价 | [storage-node](storage-node.md) |
| 每台节点的硬件和存储用量 | [inventory](inventory.md) |
| 把现有数据全量复制到冷存储要多久 | [freeze-estimate](freeze-estimate.md) |

- **inventory 和 freeze-estimate 是采集快照，** 由脚本从各节点采集生成，页首写着采集日期。
- **tiers 和 storage-node 列的是选项，** 每种买法的价格、代价都写全了，但还没有定买哪一种。
