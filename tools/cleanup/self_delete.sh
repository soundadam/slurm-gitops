#!/usr/bin/env bash
# 属主自己删 g15 / g16 上已经有副本的目录。
#
#   bash /home/nis/tianchi.liu/g15g16-cleanup/self_delete.sh
#
# 在每台要清的节点上以属主身份跑一次。清单是同目录下的 <用户名>.tsv，只取本机的行。
# 先逐目录复核：文件清单（路径 + 大小）和核对副本时记下的摘要一致才往下走，
# 任何一个对不上就什么都不删。复核通过后列出要删的目录，输入 yes 才删。
# keep 列里的小文件不在别处，删之前先拷到 ~/archive_g15g16/<host>/<目录名>/（家目录是 NFS）。
#
# 清单每行四列，制表符分隔：
#   host  dir  check  keep
#   check  list:<文件数>:<md5>  ——  find <dir> -type f -printf '%P\t%s\n' | LC_ALL=C sort | md5sum
#          top:<md5>            ——  find <dir> -mindepth 1 -maxdepth 2 | LC_ALL=C sort | md5sum（只剩 .venv 这类）
#   keep   逗号分隔的相对路径，没有写 -
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
user=$(whoami)
host=$(hostname -s)
manifest=${1:-$here/$user.tsv}

[[ -f $manifest ]] || { echo "没有 $user 的清单：$manifest" >&2; exit 1; }

rows=()
while IFS=$'\t' read -r h dir check keep; do
  [[ -z $h || $h == \#* ]] && continue
  [[ $h == "$host" ]] && rows+=("$dir"$'\t'"$check"$'\t'"$keep")
done < "$manifest"
(( ${#rows[@]} )) || { echo "$host 上没有要清的目录。"; exit 0; }

listing_md5() { find "$1" -type f -printf '%P\t%s\n' | LC_ALL=C sort | md5sum | cut -c1-32; }

echo "== $host / $user：复核"
fail=0
present=0
for row in "${rows[@]}"; do
  IFS=$'\t' read -r dir check keep <<< "$row"
  if [[ ! -d $dir ]]; then echo "  已不存在，跳过  $dir"; continue; fi
  present=$((present + 1))
  if [[ $(stat -c %U "$dir") != "$user" ]]; then echo "  属主不是 $user  $dir"; fail=1; continue; fi
  if [[ -n $(find "$dir" ! -readable -print -quit 2>/dev/null) ]]; then echo "  有读不了的文件  $dir"; fail=1; continue; fi
  case $check in
    list:*)
      IFS=: read -r _ want_n want_md5 <<< "$check"
      n=$(find "$dir" -type f | wc -l)
      got=$(listing_md5 "$dir")
      ;;
    top:*)
      want_n=-; n=-; want_md5=${check#top:}
      got=$(find "$dir" -mindepth 1 -maxdepth 2 | LC_ALL=C sort | md5sum | cut -c1-32)
      ;;
    *) echo "  清单里不认识的 check：$check" >&2; exit 1 ;;
  esac
  if [[ $n == "$want_n" && $got == "$want_md5" ]]; then
    echo "  一致  $dir  ($(du -sh "$dir" | cut -f1))"
  else
    echo "  和核对时不一样（文件数 $n / 应为 $want_n），不删  $dir"; fail=1
  fi
  for p in /proc/[0-9]*; do
    cwd=$(readlink "$p/cwd" 2>/dev/null) || continue
    [[ $cwd == "$dir" || $cwd == "$dir"/* ]] && { echo "  进程 ${p#/proc/} 的工作目录在里面  $dir"; fail=1; }
  done
done
if (( fail )); then
  echo "有目录没通过复核，什么都没删。把上面的输出发给 tianchi.liu。"; exit 1
fi
(( present )) || { echo "$host 上已经清完了。"; exit 0; }

echo
read -r -p "删掉上面标「一致」的目录？输入 yes 继续：" ans
[[ $ans == yes ]] || { echo "没删。"; exit 0; }

disk() { df -h /data/ssd0 2>/dev/null | tail -1 || true; }
disk
for row in "${rows[@]}"; do
  IFS=$'\t' read -r dir check keep <<< "$row"
  [[ -d $dir ]] || continue
  if [[ $keep != - ]]; then
    dest=~/archive_g15g16/$host/$(basename "$dir")
    IFS=, read -ra rels <<< "$keep"
    for rel in "${rels[@]}"; do
      mkdir -p "$dest/$(dirname "$rel")"
      cp -a "$dir/$rel" "$dest/$(dirname "$rel")/"
      diff -r "$dir/$rel" "$dest/$rel" > /dev/null || { echo "拷到 $dest/$rel 后对不上，停下，$dir 没删。" >&2; exit 1; }
      echo "  留存 $dest/$rel"
    done
  fi
  rm -rf -- "$dir"
  echo "  已删 $dir"
done
disk
