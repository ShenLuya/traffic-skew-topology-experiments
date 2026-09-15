# Preliminary hotspot-position results

## Scope

This pilot keeps the completed main experiment unchanged and adds hotspot nodes 3
and 27. It uses Mesh, Torus, and Fat-Tree with 64 endpoints, rates 0.06, 0.075, and
0.08, and seeds 101, 202, and 303. Node-0 means below use the same three archived
seeds for a fair preliminary comparison. Because the pilot has three seeds, the
results support manuscript drafting but are not the final statistical analysis.

## Mean packet latency (cycles)

| Topology | Rate | Node 0 baseline | Node 3 | Node 27 |
|---|---:|---:|---:|---:|
| Mesh | 0.060 | 28.79 | 27.61 | 26.66 |
| Mesh | 0.075 | 30.51 | 29.52 | 98.54 |
| Mesh | 0.080 | 68.67 | 71.58 | Unstable (3/3) |
| Torus | 0.060 | 26.92 | 26.86 | 26.78 |
| Torus | 0.075 | 40.25 | 40.30 | 56.90 |
| Torus | 0.080 | Unstable (3/3) | Unstable (3/3) | Unstable (3/3) |
| Fat-Tree | 0.060 | 13.45 | 13.45 | 13.42 |
| Fat-Tree | 0.075 | 17.13 | 15.83 | 18.06 |
| Fat-Tree | 0.080 | 88.85 | 96.68 | 86.54 |

## Conclusions that can be drafted now

1. At rate 0.06, hotspot identity has little effect in all three topologies. The
   largest difference from node 0 is about 7.4%, observed for Mesh node 27.
2. Physical hotspot position matters near saturation in Mesh. At rate 0.075, the
   interior node 27 has 3.23 times the corner node-0 latency, and at rate 0.08 all
   three node-27 runs become
   unstable while node 0 and node 3 remain stable.
3. Torus endpoints are topologically symmetric. Its node-number differences should
   be treated as finite-sample variation, not a physical edge-versus-center effect.
   All tested hotspot identities become unstable at rate 0.08.
4. Fat-Tree terminals are also symmetric under this configuration. It stays stable
   for every tested hotspot identity through rate 0.08. The three-seed confidence
   intervals near saturation are wide, so small differences must not be ranked.
5. The original node-0 main experiment remains useful, but it represents one
   hotspot placement. The pilot shows that topology conclusions near saturation
   should explicitly discuss placement sensitivity.

## Suggested manuscript wording

As a preliminary sensitivity analysis, we relocated the 20% hotspot from node 0 to
nodes 3 and 27 while preserving the 64-endpoint configuration and all other BookSim
parameters. At low offered load (0.06 flits/node/cycle), mean latency changed only
slightly across hotspot identities. Near saturation, Mesh showed a clear physical
placement effect: at a load of 0.075, the interior node-27 case reached 98.54
cycles, compared with 30.51 cycles for corner node 0, and at 0.08 all three node-27
runs exceeded the simulation's 500-cycle instability threshold. Torus became
unstable at 0.08 for all three hotspot identities, whereas Fat-Tree remained stable
through 0.08. Because Torus and Fat-Tree endpoints are topologically symmetric,
their differences across node identifiers are interpreted as finite-sample
variation rather than edge-versus-center effects. The preliminary results therefore
identify hotspot placement as an important Mesh sensitivity variable near
saturation while confirming the broader three-topology saturation trends.

## Before final submission

- Add seeds 404 and 505 for nodes 3 and 27.
- Consider one extra rate around the Mesh node-27 transition (between 0.075 and
  0.08) only if a more precise saturation boundary is needed.
- Report unstable conditions as threshold exits, not as missing observations.
- Keep the source and executable hashes with the final data archive.
