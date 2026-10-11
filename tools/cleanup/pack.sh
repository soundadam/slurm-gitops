#!/usr/bin/env bash
# 在源节点上把目录打成 tar.zst 流到冷存储，不在源盘落中间文件。
#
#   bash pack.sh <工作目录> <冷存储节点> <落点目录> <源目录>...
#
# 每个源目录：先记完整清单 <工作目录>/<host>_<目录名>.list（find -printf '%P\t%s\n'，LC_ALL=C 排序），
# 再 tar | zstd 流过去，同时记下流的 md5 到 <host>_<目录名>.md5。做完的目录留 .done，重跑时跳过。
# 工作目录放在 NFS 家目录下，冷存储那边的 verify_archive.sh 直接读。
set -euo pipefail
work=$1; node=$2; dest=$3; shift 3
mkdir -p "$work"
for src in "$@"; do
  name=$(basename "$src"); parent=$(dirname "$src")
  tag=$(hostname -s)_$name
  [[ -f $work/$tag.done ]] && { echo "skip $src"; continue; }
  echo "$(date +%T) list $src"
  find "$src" -type f -printf '%P\t%s\n' | LC_ALL=C sort > "$work/$tag.list"
  echo "$(date +%T) pack $src -> $node:$dest/$name.tar.zst ($(wc -l < "$work/$tag.list") files)"
  nice -n 19 ionice -c2 -n7 tar -C "$parent" -cf - "$name" \
    | zstd -T8 -3 -q \
    | tee >(md5sum | cut -c1-32 > "$work/$tag.md5") \
    | ssh -o BatchMode=yes "$node" "cat > '$dest/$name.tar.zst'"
  sleep 2  # 等 tee 的 md5 子进程写完
  echo "$(date +%T) done $src md5=$(cat "$work/$tag.md5")"
  touch "$work/$tag.done"
done
echo "$(date +%T) ALL DONE"
