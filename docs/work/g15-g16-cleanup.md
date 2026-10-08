# g15 / g16 清盘交接

g15、g16 的 `/data/ssd0`（各 916G）用到 99%，别人的个人目录占大头。这份文档是清盘的交接：
每个人的目录各有什么、哪些在别处有一致副本、做到哪了。冻结路线见 [migration](migration.md)，
这里是冻结之前先腾 g15 / g16 的做法。

## 做法

- 目录布局固定：`/data/ssd0/<user>/<数据集或项目>`，用户数十个、层级浅，只需 `du -sh /data/ssd0/*/*`，不做全盘扫描。
- 冷存储 g19 `/data/hdd0`（空闲约 8.8T）；落点 `/data/hdd0/<user>/archive_g15g16/<host>/`。
- 有一致副本的删，没有的迁到冷存储；**先复制、再逐文件校验、校验过才删原目录**。
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
迁移也会在目标端落成 tianchi.liu 的文件，所以冷存储上的归属要另行 `chown`。

## 各人的目录与处理

### 有一致副本，可直接删（已核对）

| 位置 | 大小 | 参照副本 | 备注 |
| --- | --- | --- | --- |
| g15 xiaobin.rong、zhiheng.wang；g16 zhiheng.wang、leyan.yang 的 `DNS3` | 各 44G | g19 `/data/ssd6/yushi.wang/Datasets/DNS3` | zhiheng 的多 5 个 `test_metrics_intrusive` 文件，先随迁 |
| g15、g16 zhiheng.wang 的 `VCTK_DEMAND` | 2G | g19 `/data/hdd0/zhiheng.wang/VCTK_DEMAND` | |
| g15 ronghui.hu `DATA/voxCeleb_1` | 38G | g19 `/data/ssd1/Benchmark/VoxCeleb1` | 前缀 `dev/wav` 不同 |
| g15 leyan.yang DNS5 | 42G | g18、g14 `dahan.wang/Datasets/DNS5_16k` | 全量哈希 350/350；布局不同，他的代码依赖布局就改迁移 |
| g16 ronghui.hu `LRAC-2025-test-data` | 1.3G | g19 `ronghui.hu/DATA/` | |

参照副本多在别人目录下，对方清掉就没了。

### 无完整副本，迁移

- g15 dong.sheng：`ears_benchmark-main` 220G（g19 的 EARS 缺 1278 个文件）、`bridge`/`logs` 106G。
- g15 leyan.yang：`Database`、`dual-unet`、`Separation` 等。
- ronghui.hu：g15 `AEC_Challenge` 45G（合成集）与 `AEC-PSE`；g16 `AEC_E2E`、`Weilai`、`SE_lightweight`、`MT_E2E`、`TASLP`。
- zhiheng.wang g16：`fiber-offload` 7G（`DNS_continuous` 见下）。
- jia.tang g16：`Data/Joint_Task_Hard_v3` 130G、`checkpoints` 18G，细节见下。
- 整体迁：jiadong.zhao、xiaobin.rong（`Datasets` 余下约 16G）、mengtong.li、zihan.gong、xiaofeng.nan、yang.xu。

## 进度

### zhiheng.wang

- g16 `DNS_continuous`（133G，222003 个文件）已经增量同步到 g9 `/data/ssd3/zhiheng.wang/temp/DNS_continuous`：
  g9 原来缺 `train_noisy` 的 57958 个文件和一个被截断的 `14042.wav`，补传 54868 个文件（35G）。
  路径加大小逐项对比零差异，557 个抽样 md5 全一致。
- 传输是 g16 直连 g9 的 rsync，用的临时 key 与 `/tmp` 里的临时文件已清除。
- 用户已同意删 g16 的原目录；**还没删，卡在上一节的权限**。
- g16 / g15 的 `DNS3`、`VCTK_DEMAND` 属有副本可删，还没动。

### jia.tang（g16，只读查看，未动）

- `Data/Joint_Task_Hard_v3` 130G：多说话人加噪声加房间混响的合成语音分离集，`train` 60000 对、`valid` 1000 对、`test` 1000 对
  （`clean/` 与 `noisy/` 各一份 wav，每个 split 一个 csv，列有说话人数、DOA、距离、SIR、噪声类型与 SNR、房间尺寸与 RT60）。
  这是他自己生成的合成集，不是公开数据集。只在 g19 上按名字找过（`maxdepth 5`），没有同名目录；g18、g14、g9、g15 还没查。
  其中 `train/` 一份 126G，csv 记录了生成参数，原则上可由他的生成脚本重建，要不要重建由他决定。
- `checkpoints` 18G：`TIDENet-SpeechRef_v6` 15G、`TIDENet-SpeechRef` 3.4G、`gtcrn_dynamic_cleaner` 585M、`TIDENet-SpeechRef_v5` 503M，另有三个几百 K 的小目录。
- `dataset/` 空，`logs/` 小。
- 下一步：等用户点名后迁到 g19 冷存储；迁前核对 `train/noisy` 与 `train/clean` 的文件数（各 60000）并逐文件校验。

## 待办

- [ ] 删 g16 上 zhiheng.wang 的 `DNS_continuous`（需要 root 或让属主删）。
- [ ] 逐人收到回复后，按上面的表出 rsync 计划，先 dry-run 再执行，校验后才删。
- [ ] 冷存储上迁过去的目录改属主。
