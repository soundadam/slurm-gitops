# slurm-gitops

aalab GPU 集群的 Slurm 方案。仓库是什么、动手前的约束在
[.claude/rules/scope.md](.claude/rules/scope.md)。

## Routing

| 要找 | 读 |
| --- | --- |
| 哪个问题去哪份文档 | [docs/README.md](docs/README.md) |
| 节点硬件与存储用量 | [docs/inventory.md](docs/inventory.md) |
| 预算分档、迁移路线 | [docs/tiers.md](docs/tiers.md)、[docs/migration.md](docs/migration.md) |
| 还差什么 | [docs/rollout.md](docs/rollout.md) |

## Commands

```sh
tools/survey.sh   # 重新采集各节点硬件，并重新生成 docs/inventory.md 与 docs/freeze-estimate.md
```

没有本地检查。
