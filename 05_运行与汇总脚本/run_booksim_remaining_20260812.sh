#!/usr/bin/env bash
set -u
cd "$HOME/booksim2"
seeds=(101 202 303 404 505)

# Complete the two missing rates in the 64-endpoint Fat-Tree data.
ft_base="formal_fattree64_20260812"
for traffic in uniform hotspotmix; do
  for rate in 0.07 0.075; do
    for seed in "${seeds[@]}"; do
      name="fattree64_${traffic}_${rate}_seed${seed}"
      cfg="$ft_base/configs/${name}.conf"
      log="$ft_base/logs/${name}.txt"
      cp clean_mesh_torus_hotspot_runs/configs/mesh_uniform_0.02.conf "$cfg"
      sed -i "s/^topology = .*/topology = fattree;/; s/^routing_function = .*/routing_function = nca;/; s/^injection_rate = .*/injection_rate = ${rate};/; s/^traffic = .*/traffic = ${traffic};/" "$cfg"
      if [[ "$traffic" == hotspotmix ]]; then
        sed -i 's/^traffic = .*/traffic = hotspot_mix({0,20});/' "$cfg"
      fi
      ./src/booksim "$cfg" seed="$seed" > "$log" 2>&1
      echo "DONE $name"
    done
  done
done

# Dragonfly uses 72 endpoints (k=2, n=1) and unit-latency links.
df_base="formal_dragonfly72_unitlat_20260812"
mkdir -p "$df_base/logs" "$df_base/configs"
rates=(0.02 0.04 0.06 0.07 0.075 0.08 0.10)
for traffic in uniform hotspotmix; do
  for rate in "${rates[@]}"; do
    for seed in "${seeds[@]}"; do
      name="dragonfly72_${traffic}_${rate}_seed${seed}"
      cfg="$df_base/configs/${name}.conf"
      log="$df_base/logs/${name}.txt"
      if [[ -s "$log" ]] && grep -q 'Total run time' "$log"; then
        echo "SKIP $name"
        continue
      fi
      cp clean_mesh_torus_hotspot_runs/configs/mesh_uniform_0.02.conf "$cfg"
      sed -i "s/^topology = .*/topology = dragonflynew;/; s/^k = .*/k = 2;/; s/^n = .*/n = 1;/; s/^routing_function = .*/routing_function = min;/; s/^injection_rate = .*/injection_rate = ${rate};/; s/^traffic = .*/traffic = ${traffic};/" "$cfg"
      if [[ "$traffic" == hotspotmix ]]; then
        sed -i 's/^traffic = .*/traffic = hotspot_mix({0,20});/' "$cfg"
      fi
      ./src/booksim "$cfg" seed="$seed" > "$log" 2>&1
      echo "DONE $name"
    done
  done
done
echo REMAINING_RUNS_COMPLETE
