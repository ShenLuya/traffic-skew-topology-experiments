#!/usr/bin/env bash
set -u

cd "$HOME/gem5"
base="formal_20260812_100m"
mkdir -p "$base"

rates=(0.01 0.02 0.04 0.06 0.08 0.10)
seeds=(101 202 303 404 505)

run_one() {
    local topology="$1"
    local traffic="$2"
    local rate="$3"
    local seed="$4"
    local name="${topology}_${traffic}_rate${rate}_seed${seed}"
    local out="$base/$name"

    if [[ -s "$out/stats.txt" ]] && grep -q 'because Network Tester completed simCycles' "$out/run.log" 2>/dev/null; then
        echo "SKIP $name"
        return 0
    fi

    mkdir -p "$out"
    local extra=()
    if [[ "$topology" == "dragonfly" ]]; then
        extra+=(--mesh-rows=4)
    fi
    if [[ "$traffic" == "hotspotmix" ]]; then
        extra+=(--hotspot-dest-id=0 --hotspot-percent=20)
    fi

    ./build/X86/gem5.opt -d "$out" \
        configs/example/garnet_synth_traffic.py \
        --network=garnet \
        --topology="$topology" \
        --num-cpus=64 \
        --num-dirs=4 \
        --injectionrate="$rate" \
        --synthetic=uniform_random \
        --routing-algorithm=0 \
        --sim-cycles=100000000 \
        --random-seed="$seed" \
        "${extra[@]}" \
        > "$out/run.log" 2>&1

    local rc=$?
    printf '%s\t%s\n' "$name" "$rc" >> "$base/status.tsv"
    echo "DONE $name rc=$rc"
}

for topology in FatTreeDirCorners dragonfly; do
    for traffic in uniform_random hotspotmix; do
        for rate in "${rates[@]}"; do
            for seed in "${seeds[@]}"; do
                run_one "$topology" "$traffic" "$rate" "$seed"
            done
        done
    done
done

echo "FORMAL_RUN_COMPLETE"
