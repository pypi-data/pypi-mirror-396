# Pylight Metrics

**Zero-Contention, High-Performance Observability for Python.**

`pylight-metrics` is a thread-safe metrics aggregator designed for high-throughput applications. It uses **Thread Local Storage (TLS)** to buffer metrics, ensuring your application's critical path remains lock-free.

## Features

- 🚀 **Zero-Contention:** Writes to thread-local buffers; global locks are only acquired during infrequent merges.
- 📊 **Rich Statistics:** Calculates P50, P90, P99, Standard Deviation, and Counts.
- 📈 **Exporters:** Supports JSON, **Prometheus**, and **CSV** (Excel) formats.
- 🔌 **Drop-in Ready:** Use decorators like `@fast_timer` and `@count_calls`.

## ⚡ Benchmarks

Comparison with `prometheus-client` (Official Library) on 50 concurrent threads.

| Metric Type | Library | Operations | Time | Speed (ops/sec) |
|------------|---------|------------|------|-----------------|
| **Timer** (P99 Calc) | `prometheus_client` | 1,000,000 | 1.70s | 585k |
| **Timer** (P99 Calc) | **pylight-metrics** | 1,000,000 | **1.27s** | **782k** |

**Result:** `pylight-metrics` is **~1.33x Faster** on the write path because it offloads heavy math (percentiles) to the background flush step.


## Installation

```bash
pip install pylight-metrics
