#!/usr/bin/env bash
set -euo pipefail

mode="${1:-smoke}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
manifest="$script_dir/run_manifest.csv"
output_dir="${RERUN_OUTPUT_DIR:-$script_dir/rerun_logs}"

if [[ "$mode" != "smoke" && "$mode" != "all" ]]; then
  echo "Usage: BOOKSIM_BIN=/absolute/path/to/booksim $0 [smoke|all]" >&2
  exit 2
fi
if [[ -z "${BOOKSIM_BIN:-}" || ! -x "$BOOKSIM_BIN" ]]; then
  echo "Set BOOKSIM_BIN to an executable BookSim binary." >&2
  exit 2
fi
if [[ ! -f "$manifest" ]]; then
  echo "Missing manifest: $manifest" >&2
  exit 2
fi

mkdir -p "$output_dir"
completed=0
skipped=0

while IFS=, read -r topology traffic rate seed base_config archived_log; do
  [[ "$topology" == "topology" ]] && continue
  if [[ "$mode" == "smoke" ]]; then
    if [[ "$topology" != "mesh" || "$traffic" != "uniform" || "$rate" != "0.02" || "$seed" != "101" ]]; then
      continue
    fi
  fi
  config="$script_dir/$base_config"
  stem="${topology}_${traffic}_rate${rate}_seed${seed}"
  log="$output_dir/${stem}.txt"
  if [[ -s "$log" ]]; then
    skipped=$((skipped + 1))
    continue
  fi
  "$BOOKSIM_BIN" "$config" "injection_rate=$rate" "seed=$seed" > "$log" 2>&1
  completed=$((completed + 1))
  echo "completed $stem"
done < "$manifest"

echo "mode=$mode completed=$completed skipped=$skipped output=$output_dir"
