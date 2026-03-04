#!/usr/bin/env bash
set -euo pipefail

# T6 — Build hygiene routine for Ren'Py projects
# Usage:
#   scripts/qa_clean_build.sh           # apply cleanup
#   scripts/qa_clean_build.sh --dry-run # preview targets only

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

print_or_exec() {
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] $*"
  else
    eval "$*"
  fi
}

echo "[T6] root: $ROOT_DIR"

# 1) Remove compiled Ren'Py bytecode that can desync traceback line mapping.
while IFS= read -r -d '' f; do
  print_or_exec "rm -f \"$f\""
done < <(find game -type f \( -name '*.rpyc' -o -name '*.rpymc' \) -print0)

# 2) Remove Python caches under project tree.
while IFS= read -r -d '' d; do
  print_or_exec "rm -rf \"$d\""
done < <(find . -type d -name '__pycache__' -print0)

# 3) Remove common build/distribution artifacts if present.
for d in "build" "dist" "tmp" ".pytest_cache"; do
  if [[ -e "$d" ]]; then
    print_or_exec "rm -rf \"$d\""
  fi
done

# 4) Report remaining compiled artifacts count.
remaining_rpyc=$(find game -type f -name '*.rpyc' | wc -l | tr -d ' ')
remaining_rpymc=$(find game -type f -name '*.rpymc' | wc -l | tr -d ' ')

if [[ $DRY_RUN -eq 1 ]]; then
  echo "[T6] dry-run finished"
else
  echo "[T6] cleanup finished"
fi

echo "[T6] remaining .rpyc:  ${remaining_rpyc}"
echo "[T6] remaining .rpymc: ${remaining_rpymc}"
