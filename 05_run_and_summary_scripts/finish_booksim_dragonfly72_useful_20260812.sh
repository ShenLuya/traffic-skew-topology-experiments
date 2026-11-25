#!/usr/bin/env bash
set -u
cd "$HOME/booksim2"
base="formal_dragonfly72_unitlat_20260812"
mkdir -p "$base/logs" "$base/configs"
seeds=(101 202 303 404 505)

run_one() {
  local traffic="$1" rate="$2" seed="$3"
  local name="dragonfly72_${traffic}_${rate}_seed${seed}"
  local cfg="$base/configs/${name}.conf"
  local log="$base/logs/${name}.txt"
  if [[ -s "$log" ]] && grep -q 'Total run time' "$log"; then
    echo "SKIP $name"
    return
  fi
  cp clean_mesh_torus_hotspot_runs/configs/mesh_uniform_0.02.conf "$cfg"
  sed -i "s/^topology = .*/topology = dragonflynew;/; s/^k = .*/k = 2;/; s/^n = .*/n = 1;/; s/^routing_function = .*/routing_function = min;/; s/^injection_rate = .*/injection_rate = ${rate};/; s/^traffic = .*/traffic = ${traffic};/" "$cfg"
  if [[ "$traffic" == hotspotmix ]]; then
    sed -i 's/^traffic = .*/traffic = hotspot_mix({0,20});/' "$cfg"
  fi
  ./src/booksim "$cfg" seed="$seed" > "$log" 2>&1
  echo "DONE $name"
}

for rate in 0.02 0.04 0.06 0.07 0.075 0.08 0.10; do
  for seed in "${seeds[@]}"; do
    run_one uniform "$rate" "$seed"
  done
done

for rate in 0.02 0.04; do
  for seed in "${seeds[@]}"; do
    run_one hotspotmix "$rate" "$seed"
  done
done

echo DRAGONFLY_USEFUL_RUNS_COMPLETE
