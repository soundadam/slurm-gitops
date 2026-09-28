# slurm-gitops

aalab GPU 集群的 Slurm 方案。仓库是什么、动手前的约束在
[.claude/rules/scope.md](.claude/rules/scope.md)。

## Routing

| 要找 | 读 |
| --- | --- |
| 哪个问题去哪份文档 | [docs/README.md](docs/README.md) |
| 节点硬件与存储用量 | [docs/inventory.md](docs/inventory.md) |
| 预算分档、冷存储配置、迁移路线 | [docs/tiers.md](docs/tiers.md)、[docs/storage-node.md](docs/storage-node.md)、[docs/migration.md](docs/migration.md) |
| 还差什么 | [docs/rollout.md](docs/rollout.md) |

## Commands

```sh
tools/survey.sh   # 重新采集各节点硬件，并重新生成 docs/inventory.md 与 docs/freeze-estimate.md
tools/feishu_docs.py push    # 把 docs/ 里定下来的几篇（名单是脚本里的 MIRRORED）单向镜像到飞书 wiki，只推有变化的页
tools/feishu_docs.py check   # 取回飞书上的页，报出被人在飞书上改过的，下次 push 覆盖
```

没有本地检查。
