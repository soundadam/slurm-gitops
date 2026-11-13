#!/usr/bin/env bash
# 属主自己删节点上已经有副本的目录。每一轮清盘部署一份到 NFS 家目录下的 <轮>-cleanup/：
#
#   bash /home/nis/tianchi.liu/g12-cleanup/self_delete.sh            # 只检查，出报告
#   bash /home/nis/tianchi.liu/g12-cleanup/self_delete.sh --delete   # 检查全过后删
#
# 在每台要清的节点上以属主身份跑。清单是同目录下的 <用户名>.tsv，只取本机的行。
# 每个目录打印三样：原目录现在扫到的文件数与大小、副本在哪与当时怎么核的、副本现在还在不在。
# 原目录和核对时记下的完整清单逐项比（路径 + 大小），对不上就列出哪些文件不一样；
# 副本当场登到副本所在节点复查（可能要输一次密码）。任何一个目录不通过，本机什么都不删。
# 报告同时存到 ~/archive_<轮>/report-<host>-<时间>.txt（g15g16-cleanup/ 的是 ~/archive_g15g16/）。
#
# 清单每行六列，制表符分隔：
#   host  dir  check  copy  verified  keep
#   check     list:<文件数>:<md5>：find <dir> -type f -printf '%P\t%s\n' | LC_ALL=C sort | md5sum；
#             完整清单在清单旁边的 <清单名>/<host>_<路径>.list，路径里的 / 换成 _
#             （g12 的 /data/ssd1/lrac_dataset → g12_data_ssd1_lrac_dataset.list；同名目录在一台机器上可以有好几份）
#   copy      tar:<节点>:<路径>:<字节数>   pack.sh 打的包，复查包在、大小不变
#             dir:<节点>:<路径>[:<前缀>=<前缀>,...]   别处的散目录，复查原目录每个文件在副本里都有、
#                                                     大小相同；两边目录前缀不同时写换算
#   verified  当时怎么核的，原样打印
#   keep      逗号分隔的相对路径（别处没有的小文件），删之前拷进 ~/archive_<轮>/<host>/<原路径>/；没有写 -
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
user=$(whoami)
host=$(hostname -s)
mode=check
args=()
for a in "$@"; do
  case $a in
    --delete) mode=delete ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    *) args+=("$a") ;;
  esac
done
manifest=${args[0]:-$here/$user.tsv}
listings=${manifest%.tsv}
[[ -f $manifest ]] || { echo "没有 $user 的清单：$manifest" >&2; exit 1; }

stash=~/archive_$(basename "$here" -cleanup)
mkdir -p "$stash"
report=$stash/report-$host-$(date +%m%d-%H%M%S).txt
exec > >(tee "$report") 2>&1

tty=/dev/null
{ : > /dev/tty; } 2>/dev/null && tty=/dev/tty
work=$(mktemp -d)
ctl=$work/ssh-%h
declare -A reach=()
cleanup() {
  for h in "${!reach[@]}"; do ssh -o ControlPath="$ctl" -O exit "$h" 2>/dev/null || true; done
  rm -rf "$work"
}
trap cleanup EXIT

human() { numfmt --to=iec --suffix=B --format=%.1f "$1"; }
total_bytes() { awk -F'\t' '{s+=$2} END{printf "%.0f", s}' "$1"; }
count() { wc -l < "$1" | tr -d ' '; }

# 扫目录，进度打在终端上，不进报告
scan() {
  find "$1" -type f -printf '%P\t%s\n' \
    | awk -v tty="$tty" -v label="$2" '{print} NR%5000==0{printf "\r    扫描中 %s … %d 个文件", label, NR > tty; fflush(tty)}' \
    | LC_ALL=C sort
  printf '\r\033[K' > "$tty"
}

# 列出两份清单的差异，每类最多 10 条
show_diff() {
  local want=$1 got=$2 n kind
  LC_ALL=C comm -23 <(cut -f1 "$want") <(cut -f1 "$got") > "$work/miss"
  LC_ALL=C comm -13 <(cut -f1 "$want") <(cut -f1 "$got") > "$work/extra"
  LC_ALL=C join -t $'\t' "$want" "$got" | awk -F'\t' '$2!=$3{print $1"  （"$2" → "$3" 字节）"}' > "$work/changed"
  for kind in miss:少了 extra:多出 changed:大小变了; do
    n=$(count "$work/${kind%%:*}")
    (( n )) || continue
    echo "            ${kind#*:} $n 个文件，例如："
    head -10 "$work/${kind%%:*}" | sed 's/^/              /'
  done
}

remote() { local h=$1; shift; ssh -o ControlPath="$ctl" "$h" "$@"; }

# 登副本所在节点，一个节点只登一次，后面复用连接
connect() {
  local h=$1
  if [[ -n ${reach[$h]:-} ]]; then [[ ${reach[$h]} == yes ]]; return; fi
  echo "    （登 $h 复查副本，要密码就输一次）"
  if ssh -o ControlMaster=yes -o ControlPath="$ctl" -o ControlPersist=30m -o ConnectTimeout=10 -fN "$h" < /dev/tty; then
    reach[$h]=yes
  else
    reach[$h]=no; return 1
  fi
}

# 复查副本，打印结果；不通过返回 1
check_copy() {
  local copy=$1 listing=$2 keep=$3 kind node path rest got nmiss nchg
  IFS=: read -r kind node path rest <<< "$copy"
  echo "    副本    $node:$path"
  connect "$node" || { echo "            现场复查：登不上 $node，没复查"; return 1; }
  case $kind in
    tar)
      got=$(remote "$node" "stat -c %s $(printf %q "$path")" 2>/dev/null) || { echo "            现场复查：包不在了"; return 1; }
      if [[ $got == "$rest" ]]; then
        echo "            现场复查：包在，$(human "$got")，大小与记录相同"
      else
        echo "            现场复查：包大小 $got 字节，记录是 $rest 字节，对不上"; return 1
      fi
      ;;
    dir)
      remote "$node" "cd $(printf %q "$path") && find . -type f -printf '%P\t%s\n'" 2>/dev/null \
        | LC_ALL=C sort > "$work/copy" || { echo "            现场复查：目录不在了"; return 1; }
      # 原目录的清单换算成副本那边的路径，去掉 keep 里的文件
      awk -F'\t' -v OFS='\t' -v maps="$rest" -v keep="$keep" '
        BEGIN { nm = split(maps, m, ","); nk = (keep == "-") ? 0 : split(keep, k, ",") }
        { for (i = 1; i <= nk; i++) if ($1 == k[i] || index($1, k[i] "/") == 1) next
          for (i = 1; i <= nm; i++) { split(m[i], ab, "="); if (index($1, ab[1]) == 1) { $1 = ab[2] substr($1, length(ab[1]) + 1); break } }
          print }' "$listing" | LC_ALL=C sort > "$work/want"
      LC_ALL=C join -t $'\t' -v1 "$work/want" "$work/copy" | cut -f1 > "$work/miss"
      LC_ALL=C join -t $'\t' "$work/want" "$work/copy" | awk -F'\t' '$2!=$3{print $1"  （"$2" → "$3" 字节）"}' > "$work/changed"
      nmiss=$(count "$work/miss"); nchg=$(count "$work/changed")
      if (( nmiss + nchg == 0 )); then
        echo "            现场复查：原目录 $(count "$work/want") 个文件在副本里都有，大小相同（副本共 $(count "$work/copy") 个文件）"
      else
        echo "            现场复查：副本里缺 $nmiss 个、大小不同 $nchg 个，例如："
        cat "$work/miss" "$work/changed" | head -10 | sed 's/^/              /'
        return 1
      fi
      ;;
    *) echo "            清单里不认识的副本类型：$kind"; return 1 ;;
  esac
}

rows=()
while IFS=$'\t' read -r h dir check copy verified keep; do
  [[ -z $h || $h == \#* ]] && continue
  [[ $h == "$host" ]] && rows+=("$dir"$'\t'"$check"$'\t'"$copy"$'\t'"$verified"$'\t'"$keep")
done < "$manifest"
(( ${#rows[@]} )) || { echo "$host 上没有要清的目录。"; exit 0; }

echo "== $host / $user：逐个复核（$(date '+%F %T')）"
fail=0
ok=()
oksize=()
i=0
for row in "${rows[@]}"; do
  IFS=$'\t' read -r dir check copy verified keep <<< "$row"
  i=$((i + 1))
  echo
  echo "[$i/${#rows[@]}] $dir"
  if [[ ! -d $dir ]]; then echo "    已不存在，跳过"; continue; fi
  bad=0
  [[ $(stat -c %U "$dir") == "$user" ]] || { echo "    属主不是 $user"; bad=1; }
  [[ -z $(find "$dir" ! -readable -print -quit 2>/dev/null) ]] || { echo "    里面有读不了的文件"; bad=1; }

  IFS=: read -r _ want_n want_md5 <<< "$check"
  listing=$listings/${host}${dir//\//_}.list
  size="?"
  if [[ ! -f $listing || $(md5sum < "$listing" | cut -c1-32) != "$want_md5" ]]; then
    echo "    核对时的清单 $listing 不在或被改过"; bad=1
  else
    scan "$dir" "$(basename "$dir")" > "$work/now"
    size=$(human "$(total_bytes "$work/now")")
    echo "    原目录  现在扫到 $(count "$work/now") 个文件，$size"
    if cmp -s "$work/now" "$listing"; then
      echo "            与核对时的清单逐项一致（$want_n 个文件，路径和大小都相同）"
    else
      echo "            和核对时的清单（$want_n 个文件）不一样："
      show_diff "$listing" "$work/now"
      bad=1
    fi
    echo "    核对    $verified"
    check_copy "$copy" "$listing" "$keep" || bad=1
  fi
  if [[ $keep != - ]]; then
    echo "    留存    别处没有的 $(tr , '\n' <<< "$keep" | wc -l) 个文件，删前拷到 $stash/$host$dir/："
    tr , '\n' <<< "$keep" | sed 's/^/              /'
  fi
  for p in /proc/[0-9]*; do
    cwd=$(readlink "$p/cwd" 2>/dev/null) || continue
    [[ $cwd == "$dir" || $cwd == "$dir"/* ]] && { echo "    进程 ${p#/proc/} 的工作目录在里面"; bad=1; }
  done
  if (( bad )); then
    echo "    结论    不通过"; fail=1
  else
    echo "    结论    可以删"; ok+=("$row"); oksize+=("$size")
  fi
done

echo
if (( fail )); then
  echo "有目录没通过，本机什么都不删。把这份报告发给 tianchi.liu：$report"; exit 1
fi
(( ${#ok[@]} )) || { echo "$host 上已经清完了。"; exit 0; }

echo "全部通过，可以删的目录："
for j in "${!ok[@]}"; do IFS=$'\t' read -r dir _ <<< "${ok[$j]}"; echo "  ${oksize[$j]}	$dir"; done
tars=()
for row in "${ok[@]}"; do
  IFS=$'\t' read -r _ _ copy _ <<< "$row"
  [[ $copy == tar:* ]] && tars+=("$copy")
done
if (( ${#tars[@]} )); then
  echo
  echo "想自己抽查包里的文件："
  for copy in "${tars[@]}"; do
    IFS=: read -r _ node path _ <<< "$copy"
    echo "  ssh $node \"zstd -dc $path | tar -tv | head\"            # 看包里前几个文件，几秒钟"
    echo "  ssh $node \"zstd -dc $path | tar -tv | grep <文件名>\"    # 找某个文件，要把整包读一遍，大包十几分钟"
  done
fi

if [[ $mode == check ]]; then
  echo
  echo "这次只检查，没删。确认要删就跑："
  echo "  bash $here/self_delete.sh --delete"
  echo "报告：$report"
  exit 0
fi

echo
read -r -p "删掉上面这些目录？输入 yes 继续：" ans < /dev/tty
echo
[[ $ans == yes ]] || { echo "没删。"; exit 0; }

disks() { df -h "$@" | awk 'NR==1 || !seen[$1]++'; }
dirs=()
for row in "${ok[@]}"; do IFS=$'\t' read -r dir _ <<< "$row"; dirs+=("$(dirname "$dir")"); done
disks "${dirs[@]}" > "$work/df_before"
for row in "${ok[@]}"; do
  IFS=$'\t' read -r dir check copy verified keep <<< "$row"
  if [[ $keep != - ]]; then
    dest=$stash/$host$dir
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
echo
echo "删之前："; cat "$work/df_before"
echo "删之后："; disks "${dirs[@]}"
echo "报告：$report"
