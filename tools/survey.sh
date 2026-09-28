#!/usr/bin/env bash
# Survey every aalab node over SSH into inventory/nodes/<node>.json, then render docs/ref/inventory.md
# and docs/ref/freeze-estimate.md.
# With --ages, also stat every file under each node's /data* into inventory/ages/<node>.json at idle IO
# priority; that walk takes an hour or two, so it runs only when asked.
# Unreachable nodes keep their previous JSON (if any) and are listed at the end.
set -uo pipefail
cd "$(dirname "$0")/.."
ages=0
[ "${1:-}" = --ages ] && ages=1
mkdir -p inventory/nodes inventory/ages

# fetch <node> <inventory subdir> <timeout s> <remote command> <script fed on stdin>
fetch() {
  local tmp; tmp=$(mktemp)
  if timeout "$3" ssh -o BatchMode=yes -o ConnectTimeout=10 "aalab.$1" "$4" < "$5" > "$tmp" 2>/dev/null \
     && python3 -m json.tool --indent 2 "$tmp" > "inventory/$2/$1.json.new"; then
    mv "inventory/$2/$1.json.new" "inventory/$2/$1.json"
  else
    rm -f "inventory/$2/$1.json.new"; echo "$1($2)" >> inventory/.unreachable
  fi
  rm -f "$tmp"
}

for n in $(seq 0 19); do
  fetch "g$n" nodes 60 "python3 -" tools/survey_node.py &
  [ $ages = 1 ] && fetch "g$n" ages 10800 "ionice -c3 nice -n19 python3 -" tools/survey_ages.py &
done
wait
[ -f inventory/.unreachable ] && { echo "unreachable: $(sort -V inventory/.unreachable | paste -sd' ')"; rm inventory/.unreachable; }
python3 tools/render_inventory.py > docs/ref/inventory.md
python3 tools/freeze_estimate.py > docs/ref/freeze-estimate.md
