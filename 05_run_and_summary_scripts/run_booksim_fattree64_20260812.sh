#!/usr/bin/env bash
set -u
cd "$HOME/booksim2"
base="formal_fattree64_20260812"
mkdir -p "$base/logs" "$base/configs"
rates=(0.01 0.02 0.04 0.06 0.08 0.10)
seeds=(101 202 303 404 505)

for traffic in uniform hotspotmix; do
  for rate in "${rates[@]}"; do
    for seed in "${seeds[@]}"; do
      name="fattree64_${traffic}_${rate}_seed${seed}"
      cfg="$base/configs/${name}.conf"
      log="$base/logs/${name}.txt"
      if [[ -s "$log" ]] && grep -q 'Total run time' "$log"; then
        continue
      fi
      cp clean_mesh_torus_hotspot_runs/configs/mesh_uniform_0.02.conf "$cfg"
      sed -i "s/^topology = .*/topology = fattree;/; s/^routing_function = .*/routing_function = nca;/; s/^injection_rate = .*/injection_rate = ${rate};/; s/^traffic = .*/traffic = ${traffic};/" "$cfg"
      if [[ "$traffic" == hotspotmix ]]; then
        sed -i 's/^traffic = .*/traffic = hotspot_mix({0,20});/' "$cfg"
      fi
      ./src/booksim "$cfg" seed="$seed" > "$log" 2>&1
      echo "$name" >> "$base/completed.txt"
    done
  done
done
echo FORMAL_FATTREE64_COMPLETE
