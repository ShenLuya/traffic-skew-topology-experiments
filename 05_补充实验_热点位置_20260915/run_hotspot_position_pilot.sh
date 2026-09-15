#!/usr/bin/env bash
set -euo pipefail

mode="${1:-all}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
booksim_bin="${BOOKSIM_BIN:-/home/shenluya/booksim2/src/booksim}"
config_dir="$script_dir/configs"
log_dir="$script_dir/logs"
mkdir -p "$config_dir" "$log_dir"

if [[ ! -x "$booksim_bin" ]]; then
  echo "BookSim executable not found: $booksim_bin" >&2
  exit 2
fi

topologies=(mesh torus fattree)
positions=(3 27)
rates=(0.06 0.075 0.08)
seeds=(101 202 303)

if [[ "$mode" == "smoke" ]]; then
  positions=(3)
  rates=(0.06)
  seeds=(101)
elif [[ "$mode" != "all" ]]; then
  echo "Usage: $0 [smoke|all]" >&2
  exit 2
fi

write_config() {
  local topology="$1"
  local position="$2"
  local rate="$3"
  local config="$4"
  local routing

  case "$topology" in
    mesh) routing="dor" ;;
    torus) routing="min_adapt" ;;
    fattree) routing="nca" ;;
    *) echo "Unknown topology: $topology" >&2; exit 2 ;;
  esac

  {
    echo "topology = $topology;"
    echo "k = 8;"
    echo "n = 2;"
    echo "routing_function = $routing;"
    echo "num_vcs = 16;"
    echo "vc_buf_size = 16;"
    echo "vc_allocator = islip;"
    echo "sw_allocator = islip;"
    echo "alloc_iters = 2;"
    echo "credit_delay = 2;"
    echo "routing_delay = 0;"
    echo "vc_alloc_delay = 1;"
    echo "sw_alloc_delay = 1;"
    echo "st_final_delay = 1;"
    echo "input_speedup = 1;"
    echo "output_speedup = 1;"
    echo "internal_speedup = 1.0;"
    echo "sim_type = latency;"
    echo "warmup_periods = 3;"
    echo "sample_period = 1000;"
    echo "sim_count = 1;"
    echo "packet_size = 1;"
    echo "traffic = hotspot_mix({${position},20});"
    echo "injection_rate = $rate;"
  } > "$config"
}

completed=0
skipped=0
for topology in "${topologies[@]}"; do
  for position in "${positions[@]}"; do
    for rate in "${rates[@]}"; do
      for seed in "${seeds[@]}"; do
        stem="${topology}_hotspot_node${position}_rate${rate}_seed${seed}"
        config="$config_dir/${stem}.conf"
        log="$log_dir/${stem}.txt"

        if [[ -s "$log" ]] && grep -q "Total run time" "$log"; then
          skipped=$((skipped + 1))
          continue
        fi

        write_config "$topology" "$position" "$rate" "$config"
        set +e
        "$booksim_bin" "$config" "seed=$seed" > "$log" 2>&1
        run_status=$?
        set -e
        if ! grep -q "Total run time" "$log"; then
          echo "BookSim failed for $stem (exit $run_status); see $log" >&2
          exit "$run_status"
        fi
        completed=$((completed + 1))
        echo "completed $stem"
      done
    done
  done
done

echo "mode=$mode completed=$completed skipped=$skipped"
