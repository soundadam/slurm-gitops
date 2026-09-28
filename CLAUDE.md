# slurm-gitops

aalab GPU 集群的 Slurm 方案。仓库是什么、动手前的约束在
[.claude/rules/scope.md](.claude/rules/scope.md)。

## Routing

| 要找 | 读 |
| --- | --- |
| 哪个问题去哪份文档 | [docs/README.md](docs/README.md) |
| 节点硬件与存储用量 | [docs/ref/inventory.md](docs/ref/inventory.md) |
| 方案、采购单、存储配置、迁移路线 | [docs/ref/plan.md](docs/ref/plan.md)、[docs/ref/purchase.md](docs/ref/purchase.md)、[docs/work/migration.md](docs/work/migration.md) |
| 还差什么 | [docs/work/rollout.md](docs/work/rollout.md) |

## Commands

```sh
tools/survey.sh   # 重新采集各节点硬件，并重新生成 docs/ref/inventory.md 与 docs/ref/freeze-estimate.md
tools/survey.sh --ages   # 另外逐个文件扫各节点 /data* 的修改与读取时间，最低 IO 优先级，要跑一两个小时
tools/feishu_docs.py push    # 把 docs/ref/ 单向镜像到飞书 wiki（ref/README.md 写进首页），只推有变化的页
tools/feishu_docs.py check   # 取回飞书上的页，报出被人在飞书上改过的，下次 push 覆盖
```

没有本地检查。
