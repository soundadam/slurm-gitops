#!/usr/bin/env bash
# 在冷存储节点上校验 pack.sh 传来的包，通过的打印 self_delete.sh 的清单行。
#
#   bash verify_archive.sh <工作目录> <源节点> <源目录> <包路径>
#
# 读一遍包，同时核两样：包的 md5 等于源端流的 md5；解包（zstd 核对帧校验）列出的普通文件
# 路径和大小与源端清单逐项相同。不逐文件算 md5。tar 列完后把流读空，md5 和 zstd 的帧校验才覆盖整个包。
set -euo pipefail
work=$1; srchost=$2; src=$3; archive=$4
name=$(basename "$src")
tag=${srchost}_$name
list=$work/$tag.list

tee >(md5sum | cut -c1-32 > "$work/$tag.got") < "$archive" \
  | zstd -dc \
  | { tar -tvf - --quoting-style=literal --numeric-owner; cat > /dev/null; } \
  | awk -v top="$name/" '/^-/ { size = $3; for (i = 0; i < 5; i++) sub(/^[^ ]+ +/, ""); if (index($0, top) == 1) print substr($0, length(top) + 1) "\t" size }' \
  | LC_ALL=C sort > "$work/$tag.inarchive"
sleep 2  # 等 tee 的 md5 子进程写完
got=$(cat "$work/$tag.got"); rm "$work/$tag.got"
want=$(cat "$work/$tag.md5")
[[ $got == "$want" ]] || { echo "$archive：md5 $got，源端流是 $want" >&2; exit 1; }
if ! cmp -s "$work/$tag.inarchive" "$list"; then
  echo "$archive：包里的清单和源端不一样" >&2
  diff "$list" "$work/$tag.inarchive" | head -20 >&2
  exit 1
fi
rm "$work/$tag.inarchive"

n=$(wc -l < "$list" | tr -d ' ')
printf '%s\t%s\tlist:%s:%s\ttar:%s:%s:%s\t%s 解包核对：%s 个文件路径和大小与原目录逐项一致；包 md5 %s 与源端流一致\t-\n' \
  "$srchost" "$src" "$n" "$(md5sum < "$list" | cut -c1-32)" \
  "$(hostname -s)" "$archive" "$(stat -c %s "$archive")" "$(date +%m-%d)" "$n" "$got"
