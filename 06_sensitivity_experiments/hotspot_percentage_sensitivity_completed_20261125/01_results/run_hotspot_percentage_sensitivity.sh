#!/usr/bin/env bash
set -euo pipefail

mode="${1:-smoke}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
default_booksim_bin="$(cd "$script_dir/../02_booksim2_reproduction_environment/src" && pwd)/booksim"
booksim_bin="${BOOKSIM_BIN:-$default_booksim_bin}"
run_timeout="${RUN_TIMEOUT_SECONDS:-180}"

if [[ ! -x "$booksim_bin" ]]; then
  echo "BookSim executable not found: $booksim_bin" >&2
  exit 2
fi

if [[ "$mode" == "smoke" ]]; then
  config_dir="$script_dir/smoke_configs"
  log_dir="$script_dir/smoke_logs"
  manifest="$script_dir/smoke_manifest.csv"
  topologies=(mesh)
  percentages=(20)
  rates=(0.02)
  seeds=(101)
elif [[ "$mode" == "all" ]]; then
  config_dir="$script_dir/configs"
  log_dir="$script_dir/logs"
  manifest="$script_dir/run_manifest.csv"
  topologies=(mesh torus fattree)
  percentages=(10 20 30 40)
  rates=(0.02 0.03 0.04)
  seeds=(101 202 303 404 505)
else
  echo "Usage: $0 [smoke|all]" >&2
  exit 2
fi

mkdir -p "$config_dir" "$log_dir"

write_config() {
  local topology="$1"
  local percentage="$2"
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
    echo "traffic = hotspot_mix({0,${percentage}});"
    echo "injection_rate = $rate;"
  } > "$config"
}

write_provenance() {
  local booksim_root
  booksim_root="$(cd "$(dirname "$booksim_bin")/.." && pwd)"
  {
    echo "run_mode=$mode"
    echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "booksim_binary=$booksim_bin"
    echo "booksim_binary_sha256=$(sha256sum "$booksim_bin" | awk '{print $1}')"
    echo "booksim_git_head=$(git -C "$booksim_root" rev-parse HEAD 2>/dev/null || echo unavailable)"
    echo "traffic_cpp_sha256=$(sha256sum "$booksim_root/src/traffic.cpp" | awk '{print $1}')"
    echo "traffic_hpp_sha256=$(sha256sum "$booksim_root/src/traffic.hpp" | awk '{print $1}')"
    echo "compiler=$(g++ --version | head -1)"
    echo "run_timeout_seconds=$run_timeout"
  } > "$script_dir/provenance_${mode}.txt"
}

printf 'run_id,topology,routing,hotspot_percentage,injection_rate,seed,config_file,log_file\n' > "$manifest"
total=$((${#topologies[@]} * ${#percentages[@]} * ${#rates[@]} * ${#seeds[@]}))
index=0
completed=0
skipped=0

write_provenance

for topology in "${topologies[@]}"; do
  case "$topology" in
    mesh) routing="dor" ;;
    torus) routing="min_adapt" ;;
    fattree) routing="nca" ;;
  esac
  for percentage in "${percentages[@]}"; do
    for rate in "${rates[@]}"; do
      for seed in "${seeds[@]}"; do
        index=$((index + 1))
        stem="${topology}_hotspot${percentage}_rate${rate}_seed${seed}"
        if [[ "$mode" == "smoke" ]]; then
          stem="smoke_${stem}"
        fi
        config="$config_dir/${stem}.conf"
        log="$log_dir/${stem}.txt"
        exit_file="$log_dir/${stem}.exitcode"

        write_config "$topology" "$percentage" "$rate" "$config"
        printf '%s,%s,%s,%s,%s,%s,%s,%s\n' \
          "$stem" "$topology" "$routing" "$percentage" "$rate" "$seed" \
          "${config#"$script_dir/"}" "${log#"$script_dir/"}" >> "$manifest"

        if [[ -s "$log" ]] && grep -q "Total run time" "$log"; then
          skipped=$((skipped + 1))
          echo "[$index/$total] skipped $stem"
          continue
        fi

        set +e
        timeout "$run_timeout" "$booksim_bin" "$config" "seed=$seed" > "$log" 2>&1
        run_status=$?
        set -e
        printf '%s\n' "$run_status" > "$exit_file"

        if ! grep -q "Total run time" "$log"; then
          echo "BookSim did not finish $stem (exit $run_status); see $log" >&2
          exit "$run_status"
        fi

        completed=$((completed + 1))
        echo "[$index/$total] completed $stem"
      done
    done
  done
done

if [[ "$mode" == "smoke" ]]; then
  smoke_log="$log_dir/smoke_mesh_hotspot20_rate0.02_seed101.txt"
  grep -q '^Packet latency average = 28.3384 (1 samples)$' "$smoke_log"
  grep -q '^Injected flit rate average = 0.0194062 (1 samples)$' "$smoke_log"
  grep -q '^Accepted flit rate average = 0.0193646 (1 samples)$' "$smoke_log"
  echo "SMOKE_VERIFIED latency=28.3384 injected=0.0194062 accepted=0.0193646"
fi

echo "mode=$mode total=$total completed=$completed skipped=$skipped"
