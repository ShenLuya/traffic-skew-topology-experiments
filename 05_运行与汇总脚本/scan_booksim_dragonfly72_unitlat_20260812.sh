#!/usr/bin/env bash
set -u
cd "$HOME/booksim2"
base="scan_dragonfly72_unitlat_20260812"
mkdir -p "$base/logs" "$base/configs"
rates=(0.02 0.04 0.06 0.08 0.10)

for traffic in uniform hotspotmix; do
  for rate in "${rates[@]}"; do
    name="dragonfly72_${traffic}_${rate}_seed101"
    cfg="$base/configs/${name}.conf"
    log="$base/logs/${name}.txt"
    cp clean_mesh_torus_hotspot_runs/configs/mesh_uniform_0.02.conf "$cfg"
    sed -i "s/^topology = .*/topology = dragonflynew;/; s/^k = .*/k = 2;/; s/^n = .*/n = 1;/; s/^routing_function = .*/routing_function = min;/; s/^injection_rate = .*/injection_rate = ${rate};/; s/^traffic = .*/traffic = ${traffic};/" "$cfg"
    if [[ "$traffic" == hotspotmix ]]; then
      sed -i 's/^traffic = .*/traffic = hotspot_mix({0,20});/' "$cfg"
    fi
    ./src/booksim "$cfg" seed=101 > "$log" 2>&1
    status=STABLE
    grep -q 'Simulation unstable' "$log" && status=UNSTABLE
    latency=$(grep 'Packet latency average = .* (1 samples)' "$log" | tail -1 | sed -E 's/.*= ([^ ]+).*/\1/')
    echo "$traffic,$rate,$status,$latency"
  done
done
