# 热点比例敏感性实验报告

## 1. 结论摘要

本批次 180 次 BookSim2 运行已全部执行并解析，36 个实验单元完整。新实验中与历史 20% 热点数据重合的 30 次运行实现了逐种子、逐指标 **30/30 精确一致**，说明本次恢复的 `hotspot_mix` 实现、配置和旧实验方法一致。

在目的端理论负载低于 1 flit/cycle 的 33 个实验单元中，165 次运行均达到 BookSim 收敛停止条件。唯一越过理论目的端上限的条件是 `40% hotspot × 0.04 injection rate`，其负载为

\[
64 \times 0.40 \times 0.04 = 1.024\ \text{flits/cycle}.
\]

该条件下三种拓扑–路由配置均明显恶化，但运行状态不同：Mesh–`dor` 和 Fat-Tree–`nca` 各有 4/5 次达到十个采样阶段上限；Torus–`min_adapt` 有 2/5 次达到采样上限、3/5 次触发 500-cycle 阈值退出。因此，论文不能把这 13 次运行称为“全部收敛”，也不能把 Torus 的三次阈值退出赋值为 500 cycles。

## 2. Material Passport

- 模拟器：BookSim2，Git commit `28f43299f1706a3160ffac721ca461d74eb6e618`
- BookSim 二进制 SHA-256：`f5e8b8b6e2e87ef9794558158464d292b58fd1eee14cd207aa9dcc7a1c59700a`
- `traffic.cpp` SHA-256：`874207df0277ad9e12bc2651d2c62c3e2b2994c82378158a10d9e463cf456900`
- `traffic.hpp` SHA-256：`a677db0789a8e201343b8b9f22874f56609f084ed0a9c98c6fbafe3d8e170261`
- 编译器：g++ 14.2.0
- 网络规模：64 endpoints；Mesh/Torus 使用 `k=8, n=2`
- 配置：Mesh–`dor`、Torus–`min_adapt`、Fat-Tree–`nca`
- 流控：16 VCs，每 VC 16-flit buffer
- 分配器：`islip` VC/switch allocator，`alloc_iters=2`
- packet size：1 flit
- traffic：`hotspot_mix({0,p})`，node 0 为热点；其余流量均匀分布到另外 63 个节点
- 热点比例：10%、20%、30%、40%
- 注入率：0.02、0.03、0.04 flits/node/cycle
- seeds：101、202、303、404、505
- 停止协议：latency mode；3 个 warmup periods；1,000-cycle sample period；最多 10 个采样阶段；500-cycle latency threshold
- 运行总数：`4 × 3 × 3 × 5 = 180`
- 单次外部超时：180 s；没有外部超时或脚本崩溃
- 执行窗口：2026-11-25 21:28:34–21:30:29（本机时间，约 115 s wall time）

## 3. 审计结果

| 状态 | Mesh | Torus | Fat-Tree | 合计 |
|---|---:|---:|---:|---:|
| converged stop | 56 | 55 | 56 | 167 |
| maximum-sample stop | 4 | 2 | 4 | 10 |
| threshold exit | 0 | 3 | 0 | 3 |
| 合计 | 60 | 60 | 60 | 180 |

BookSim2 此版本在 `TrafficManager::Run()` 成功时由 `main` 返回 `-1`，在 Linux sidecar 中表现为 process exit code 255；因此这里的 177 个 code-255 不是程序崩溃。三次 code-0 对应明确打印 `Simulation unstable, ending ...` 的 threshold exits。

## 4. 汇总结果（mean packet latency, cycles）

以下均值基于五个 seeds；`*` 表示该单元含 maximum-sample stop，不能解释为严格稳态均值；`†` 表示只有两次 maximum-sample runs 有最终统计，另三次为 threshold exits。

| 配置 | 注入率 | 10% | 20% | 30% | 40% |
|---|---:|---:|---:|---:|---:|
| Mesh–dor | 0.02 | 27.55 | 28.43 | 29.10 | 29.79 |
| Mesh–dor | 0.03 | 27.56 | 28.36 | 29.25 | 30.55 |
| Mesh–dor | 0.04 | 27.65 | 28.46 | 29.72 | 90.65* |
| Torus–min_adapt | 0.02 | 26.14 | 26.10 | 26.19 | 26.31 |
| Torus–min_adapt | 0.03 | 26.12 | 26.20 | 26.50 | 27.46 |
| Torus–min_adapt | 0.04 | 26.12 | 26.38 | 27.14 | 174.54† |
| Fat-Tree–nca | 0.02 | 13.08 | 13.04 | 13.12 | 13.22 |
| Fat-Tree–nca | 0.03 | 13.07 | 13.12 | 13.23 | 13.83 |
| Fat-Tree–nca | 0.04 | 13.05 | 13.16 | 13.58 | 117.54* |

95% Student-t confidence intervals and per-cell status counts are retained in `summary.csv`.

## 5. 科学解释边界

公式能够预先指出目的端的必要容量边界：当 `64 × p × λ > 1` 时，热点目的端收到的 offered load 已超过每周期一 flit 的上限。它不能预测三种配置的具体延迟、谁先退化、seed 波动、是否满足 BookSim 收敛停止条件，或 routing 引起的内部拥塞差异。新实验的价值正是检验边界前后的实际行为，并显示三种 topology–routing configurations 在过载条件下的有限运行表现不同。

在论文中建议将 `40% × 0.04` 表述为“analytically overloaded stress condition”，将图中的空心菱形称为“finite-run estimates”，并明确 Torus 的三次 threshold exits 没有最终延迟统计。不要将 90.65、174.54 和 117.54 cycles 当作已经证明的稳态延迟进行排名。

## 6. 产物

- `raw_runs.csv`：180 次逐运行结果、状态、速率和路径
- `summary.csv`：36 个实验单元、95% t interval 和理论负载边界
- `historical_20pct_comparison.csv`：30 次历史复现对照
- `verification_report.txt`：自动核验摘要
- `figures/hotspot_percentage_latency.pdf`：论文矢量图
- `figures/hotspot_percentage_latency.png`：300 dpi 预览图
- `configs/`、`logs/`：全部配置、原始日志和 exit-code sidecars
- `provenance_all.txt`：可复现性记录

历史数据和现有论文文件均未被覆盖。
