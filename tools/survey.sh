#!/usr/bin/env bash
# Survey every aalab node over SSH into inventory/nodes/<node>.json, then render docs/inventory.md.
# Unreachable nodes keep their previous JSON (if any) and are listed at the end.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p inventory/nodes
unreachable=()
for n in $(seq 0 19); do
  (
    tmp=$(mktemp)
    if timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 "aalab.g$n" python3 - < tools/survey_node.py > "$tmp" 2>/dev/null \
       && python3 -m json.tool --indent 2 "$tmp" > "inventory/nodes/g$n.json.new"; then
      mv "inventory/nodes/g$n.json.new" "inventory/nodes/g$n.json"
    else
      rm -f "inventory/nodes/g$n.json.new"; echo "g$n" >> inventory/.unreachable
    fi
    rm -f "$tmp"
  ) &
done
wait
[ -f inventory/.unreachable ] && { echo "unreachable: $(sort -V inventory/.unreachable | paste -sd' ')"; rm inventory/.unreachable; }
python3 tools/render_inventory.py > docs/inventory.md
