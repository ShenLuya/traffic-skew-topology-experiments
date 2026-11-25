# Hotspot-Percentage Sensitivity: Interpretation Notes

## Purpose

This supplementary analysis tests whether conclusions drawn from the 20% hotspot main experiment remain stable when hotspot intensity changes. It does not replace the 210-run main experiment and does not treat 20% as a uniquely correct workload value.

The batch contains 180 executions. Thirty runs at 20% hotspot share and injection rates 0.02/0.04 exactly overlap historical main-experiment configurations and reproduce their run-level metrics (30/30). The remaining 150 executions cover new parameter combinations. The batch should therefore be described as a 180-run sensitivity and reproducibility experiment, while noting the historical overlap rather than counting it as new independent evidence.

## Supported findings

1. All 165 runs in the 33 cells below the necessary destination-service bound reached converged stops.
2. At injection rates 0.02 and 0.03, latency changes gradually as hotspot share rises from 10% to 40%; the data do not identify a special transition at 20%.
3. At 40% hotspot share and injection rate 0.04, the offered hotspot load is `64 x 0.40 x 0.04 = 1.024 flits/cycle`, slightly above the analytical service bound.
4. In that overloaded cell, Mesh-`dor` and Fat-Tree-`nca` each produce five final finite-run statistics but four maximum-sample stops. Torus-`min_adapt` produces two maximum-sample statistics and three threshold exits.
5. These overloaded values characterize run outcomes under a finite stress protocol; they are not comparable steady-state latency estimates and do not establish that Torus is generally worst.

## Why the experiment remains necessary despite the formula

The formula identifies when the shared destination is necessarily overloaded. It cannot predict topology-routing-specific latency, seed variation, internal congestion, or BookSim stop outcomes. The simulation measures those quantities and checks behavior on both sides of the analytical boundary.

## Relationship to manuscript claims

- Treat 20% as a controlled, moderate skew level used for the full seven-rate main comparison.
- Describe the 10%-40% sweep as supplementary sensitivity analysis at three deliberately selected low rates.
- Keep the 210 main runs separate from the 180 sensitivity/reproducibility executions.
- Do not compute a new LDF from this sweep because it has no separately paired uniform baseline for every hotspot share.
- Replace any limitation stating that the entire study uses only one 20% hotspot probability. The main comparison uses 20%, while the supplementary sweep covers 10%-40%.
- Continue to describe the objects being compared as topology-routing configurations because routing remains topology-specific.
- Do not describe this synthetic traffic as a measured big-data workload trace.

## Figure interpretation

Filled markers represent cells in which all five seeds reached converged stops, with 95% Student-t intervals. Open diamonds represent finite-run estimates from cells containing maximum-sample stops. Crosses mark threshold exits and are status symbols, not latency values. The analytical boundary annotation identifies the overloaded 40%-at-0.04 condition.
