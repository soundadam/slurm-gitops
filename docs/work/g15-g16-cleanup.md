# g15 / g16 清盘交接

g15、g16 的 `/data/ssd0`（各 916G）用到 99%，别人的个人目录占大头。这份文档是清盘的交接：
每个人的目录各有什么、哪些在别处有一致副本、做到哪了。冻结路线见 [migration](migration.md)，
这里是冻结之前先腾 g15 / g16 的做法。

## 做法

- 目录布局固定：`/data/ssd0/<user>/<数据集或项目>`，用户数十个、层级浅，只需 `du -sh /data/ssd0/*/*`，不做全盘扫描。
- 冷存储 g19 `/data/hdd0`（空闲约 8.8T）；落点 `/data/hdd0/<user>/archive_g15g16/<host>/`。
- 有一致副本的删，没有的迁到冷存储；**先复制、再逐文件校验、校验过才删原目录**。
  迁冷存储怎么打包、怎么校验见 [cold-archive](../../.claude/rules/cold-archive.md)。
- **逐人由用户点名才动**；没回复的人不设默认处理。g19 上的公共 DNS3 / DNS5 / VoxCeleb1 不动。
- 校验：`find . -type f -printf '%P\t%s\n' | sort` 比路径加大小，再每 400 个文件抽一个 `md5sum`；
  DNS5 这类文件大小全一样的整套哈希。增量补传用 `rsync -a --size-only --files-from`。
- 节点间的别名是 `aalab.g15` 这种，裸 `g15` 在 elon 上解析不了；集群内部 `g9`、`g9.nca` 可解析。
- 家目录 `/home/nis/tianchi.liu` 是 NFS，所有节点共享。
- 不要 `pkill -f`：模式会匹配到 ssh 外壳自己的命令行，把自己杀掉。

## 权限（卡住的地方）

集群账号 `tianchi.liu` 在 g16 上对别人的目录只有读：`/data/ssd0/zhiheng.wang/DNS_continuous` 及其子目录属主是 zhiheng.wang，
权限 `drwxr-xr-x`，`sudo` 要密码。因此 **删别人的原目录需要 root 或属主自己动手**；
在节点上动 root 之前先问用户（见 [scope](../../.claude/rules/scope.md)）。
所以删除交给属主：每个人同步、校验完，发给他 [`tools/cleanup/self_delete.sh`](../../tools/cleanup/self_delete.sh)
和他的清单 `tools/cleanup/<user>.tsv`，部署在 NFS `/home/nis/tianchi.liu/g15g16-cleanup/`，旁边的 `<user>/` 放核对时的完整文件清单
（几十万行，不进仓）。他在每台节点上先跑 `bash /home/nis/tianchi.liu/g15g16-cleanup/self_delete.sh` 只检查，
看过报告再加 `--delete`。脚本逐目录打印原目录现在的文件数与大小、副本在哪与当时怎么核的，原目录与完整清单逐项比，
对不上就列出是哪些文件；副本当场登到副本节点复查。有一项不通过就整机不删。清单格式见脚本开头。
迁冷存储的目录用 [`pack.sh`](../../tools/cleanup/pack.sh) 在源端打包流过去，
冷存储上 [`verify_archive.sh`](../../tools/cleanup/verify_archive.sh) 校验通过后直接打印清单行。
迁移也会在目标端落成 tianchi.liu 的文件，所以冷存储上的归属要另行 `chown`；
在那之前落点目录建成 setgid、组可写（g19 上成员同属 gid 1000），属主自己能挪、能删。

## 各人的目录与处理

### 有一致副本，可直接删（已核对）

| 位置 | 大小 | 参照副本 | 备注 |
| --- | --- | --- | --- |
| g15 xiaobin.rong、zhiheng.wang；g16 zhiheng.wang、leyan.yang 的 `DNS3` | 各 44G | g19 `/data/ssd6/yushi.wang/Datasets/DNS3` | zhiheng 的多 5 个 `test_metrics_intrusive` 文件，先随迁 |
| g15、g16 zhiheng.wang 的 `VCTK_DEMAND` | 2G | g19 `/data/hdd0/zhiheng.wang/VCTK_DEMAND` | 多一个 `trINFO_all.csv`（1.7M） |
| g15、g16 zhiheng.wang 的 `fiber-offload` | 各 6.8G | g19 `/data/hdd0/zhiheng.wang/fiber-offload` | 只剩两个 `.venv`，他 9-13 自己迁过（有 `COPY_COMPLETE`） |
| g15 ronghui.hu `DATA/voxCeleb_1` | 38G | g19 `/data/ssd1/Benchmark/VoxCeleb1` | 前缀 `dev/wav` 不同 |
| g15 leyan.yang DNS5 | 42G | g18、g14 `dahan.wang/Datasets/DNS5_16k` | 全量哈希 350/350；布局不同，他的代码依赖布局就改迁移 |
| g16 ronghui.hu `LRAC-2025-test-data` | 1.3G | g19 `ronghui.hu/DATA/` | |

参照副本多在别人目录下，对方清掉就没了。

### 无完整副本，迁移

- g15 dong.sheng：`ears_benchmark-main` 220G（g19 的 EARS 缺 1278 个文件）、`bridge`/`logs` 106G。
- g15 leyan.yang：`Database`、`dual-unet`、`Separation` 等。
- ronghui.hu：g15 `AEC_Challenge` 45G（合成集）与 `AEC-PSE`；g16 `AEC_E2E`、`Weilai`、`SE_lightweight`、`MT_E2E`、`TASLP`。
- jia.tang g16：`Data/Joint_Task_Hard_v3` 130G、`checkpoints` 18G，细节见下。
- 整体迁：jiadong.zhao、xiaobin.rong（`Datasets` 余下约 16G）、mengtong.li、zihan.gong、xiaofeng.nan、yang.xu。

## 进度

### zhiheng.wang

- g16 `DNS_continuous`（133G，222003 个文件）已经增量同步到 g9 `/data/ssd3/zhiheng.wang/temp/DNS_continuous`：
  g9 原来缺 `train_noisy` 的 57958 个文件和一个被截断的 `14042.wav`，补传 54868 个文件（35G）。
  路径加大小逐项对比零差异，557 个抽样 md5 全一致。
- 传输是 g16 直连 g9 的 rsync，用的临时 key 与 `/tmp` 里的临时文件已清除。
- g15 上有 `DNS3`、`VCTK_DEMAND`、`fiber-offload`，g16 上另有 `DNS_continuous`，四样都有副本（见上表），没有要迁的。
  10-08 对过参照副本：清单摘要（路径 + 大小）与 g15、g16 一致，只差 `DNS3/test_metrics_intrusive/` 5 个文件和
  `VCTK_DEMAND/trINFO_all.csv`，两台上这几个文件 md5 相同。
- 10-08 他在 g15、g16 上跑完脚本，两台上他的目录已空；留存的 6 个小文件在他家目录 `~/archive_g15g16/{g15,g16}/`，md5 与原件一致。
  删后复查过参照副本仍在：g9 的 `DNS_continuous` 清单摘要不变，g19 的 `VCTK_DEMAND`、`fiber-offload`、`DNS3` 都在。**zhiheng.wang 清完。**

### jia.tang（g16）

- `Data/Joint_Task_Hard_v3` 130G：多说话人加噪声加房间混响的合成语音分离集，`train` 60000 对、`valid` 1000 对、`test` 1000 对
  （`clean/` 与 `noisy/` 各一份 wav，每个 split 一个 csv，列有说话人数、DOA、距离、SIR、噪声类型与 SNR、房间尺寸与 RT60）。
  这是他自己生成的合成集，不是公开数据集。只在 g19 上按名字找过（`maxdepth 5`），没有同名目录；g18、g14、g9、g15 还没查。
  其中 `train/` 一份 126G，csv 记录了生成参数，原则上可由他的生成脚本重建，要不要重建由他决定。
- `checkpoints` 18G：`TIDENet-SpeechRef_v6` 15G、`TIDENet-SpeechRef` 3.4G、`gtcrn_dynamic_cleaner` 585M、`TIDENet-SpeechRef_v5` 503M，另有三个几百 K 的小目录。
- `dataset/`、`logs/` 是空目录。
- 10-08 整个 `/data/ssd0/jia.tang/` 迁到 g19 `/data/hdd0/jia.tang/archive_g15g16/g16/`：g16 直连 g19 rsync，125385 个文件 158.6 GB，
  train / valid / test 的 noisy 与 clean 各 60000 / 1000 / 1000。
  校验：`Data`（124003 个文件）、`checkpoints`（1382 个）的清单摘要两边一致；checkpoints 全部、3 个 csv、wav 每 400 抽 1，共 1695 个 md5 全一致。
  临时 key 已从 `authorized_keys` 撤掉。
- 之后在 g19 本机把 `Data` 打成 `Data.tar.zst`（109G），解一遍列出的 124003 个文件路径和大小与散文件一致，散文件已删。
  g19 上现在是 `Data.tar.zst`、`checkpoints/`（散着，大文件）和两个空目录。
- 他在 g16 上跑完脚本，`Data`、`checkpoints` 已删，只剩两个空目录。**jia.tang 清完。**

### ronghui.hu（g15、g16）

- 10-11 开始迁：g15 `AEC-PSE`、`DATA/AEC_Challenge`，g16 `AEC_Challenge`、`LRAC/TASLP`、`AEC_Weilai`、`SE_lightweight`、`MT_E2E`、`AEC_E2E`，
  各打成一个包流到 g19 `/data/hdd0/ronghui.hu/archive_g15g16/<host>/`，约 410G。
- `DATA/voxCeleb_1`、`LRAC/LRAC-2025-test-data` 有副本（见上表），不迁，进清单直接删；g16 根下一个 2.3M 的 wav 由他自己处理。
- 8 个包共 238G，在 g19 上逐个解包核对，文件路径和大小与原目录逐项一致，包 md5 与源端流一致。
- `voxCeleb_1` 对 g19 `/data/ssd1/Benchmark/VoxCeleb1`：除 `vox1_meta.csv`、`voxceleb1_test_v2.txt` 外文件全在、大小相同，抽 384 个 md5 一致；
  `LRAC-2025-test-data` 对 g19 `/data/ssd6/ronghui.hu/DATA/LRAC-2025-test-data`：5331 个文件全在，抽 265 个 md5 一致，
  他用 `change_path.py` 改过路径的 16 个 csv/scp 与这个脚本两边不同。这几个小文件进清单的 keep 列，删前拷进他家目录。
- 清单 `tools/cleanup/ronghui.hu.tsv` 已部署，以 tianchi.liu 预跑过只检查模式，除属主一项外全部通过。他删完 g15 腾约 100G、g16 约 340G。

## 待办

- [ ] ronghui.hu 在 g15、g16 上跑 `self_delete.sh`，看过报告再 `--delete`。
- [ ] 逐人收到回复后，按上面的表出迁移计划，先 dry-run 再执行，校验后才删。
- [ ] 冷存储上迁过去的目录改属主。
