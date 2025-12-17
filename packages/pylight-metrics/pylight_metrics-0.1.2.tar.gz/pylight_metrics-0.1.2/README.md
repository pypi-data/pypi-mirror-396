# Pylight Metrics

**Zero-Contention, High-Performance Observability for Python.**

`pylight-metrics` is a thread-safe metrics aggregator designed for high-throughput applications. It uses **Thread Local Storage (TLS)** to buffer metrics, ensuring your application's critical path remains lock-free.

## Features

- 🚀 **Zero-Contention:** Writes to thread-local buffers; global locks are only acquired during infrequent merges.
- 📊 **Rich Statistics:** Calculates P50, P90, P99, Standard Deviation, and Counts.
- 📈 **Exporters:** Supports JSON, **Prometheus**, and **CSV** (Excel) formats.
- 🔌 **Drop-in Ready:** Use decorators like `@fast_timer` and `@count_calls`.

## Installation

```bash
pip install pylight-metrics
