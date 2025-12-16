
# Telemetry Harbor Python SDK

![PyPI](https://img.shields.io/pypi/v/telemetryharborsdk.svg)
![Python Versions](https://img.shields.io/pypi/pyversions/telemetryharborsdk.svg)
![Downloads](https://img.shields.io/pypi/dm/telemetryharborsdk.svg)
![License](https://img.shields.io/pypi/l/telemetryharborsdk.svg)

![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)
![Stars](https://img.shields.io/github/stars/TelemetryHarbor/harbor-sdk-python.svg?style=social)

## The Easiest Way to Visualize Python Data 🚀

**Stop managing InfluxDB and Grafana containers.**

The **Telemetry Harbor SDK** lets you send telemetry from any Python application (Raspberry Pi, Servers, Desktop scripts) to a fully managed Grafana dashboard in **1 line of code**.

* **⚡ Instant Visualization:** Data appears on your hosted Grafana dashboard in milliseconds.
* **💾 Infinite Storage:** We handle the time-series database for you.
* **🔌 Zero Config:** No Docker, no ports, no firewall rules. Just `pip install`.

[**👉 Get your Free API Key at TelemetryHarbor.com**](https://www.telemetryharbor.com)

---

## Installation

```bash
pip install telemetryharborsdk
````

-----

## 30-Second Quickstart

1.  **Get a Key:** Sign up at [TelemetryHarbor.com](https://www.telemetryharbor.com) (Free Tier includes 3M data points).
2.  **Run this script:**

<!-- end list -->

```python
from telemetryharborsdk import HarborClient, GeneralReading

# 1. Initialize (Replace with your actual ID and Key)
client = HarborClient(
    endpoint="https://telemetryharbor.com/api/v2/ingest/YOUR_HARBOR_ID",
    api_key="sk_live_..."
)

# 2. Send Data (No database schema required)
client.send(GeneralReading(
    ship_id="raspberry-pi-4",    # Your Device Name
    cargo_id="temperature",      # Your Metric Name
    value=42.5
))

print("Data sent! Check your Grafana dashboard.")
```

-----

## Advanced Usage

### Sending Batches (Faster)

If you have high-frequency data, use `send_batch` to upload multiple readings in one HTTP request.

```python
batch = [
    GeneralReading(ship_id="sensor-1", cargo_id="temp", value=22.5),
    GeneralReading(ship_id="sensor-1", cargo_id="humidity", value=60.1),
    GeneralReading(ship_id="sensor-1", cargo_id="voltage", value=3.3),
]

client.send_batch(batch)
```

### Logging GPS Data

Telemetry Harbor automatically groups GPS data for map visualizations. Send `latitude` and `longitude` as separate metrics with the same timestamp.

```python
# The SDK handles the timestamps automatically if you don't provide one
client.send_batch([
    GeneralReading(ship_id="truck-01", cargo_id="latitude", value=41.123),
    GeneralReading(ship_id="truck-01", cargo_id="longitude", value=29.456)
])
```

> **Pro Tip:** In Grafana, use the "Geomap" panel to visualize this instantly.

-----

## Features

  * ✅ **Pydantic Validation:** Never send bad data again.
  * ✅ **Auto-Retry:** Built-in exponential backoff for flaky networks (perfect for IoT/Edge).
  * ✅ **Async Ready:** Designed for high-throughput logging.
  * ✅ **Type Hinting:** Full support for modern Python IDEs.

-----

## Need Help?

  * 📚 **Documentation:** [docs.telemetryharbor.com](https://docs.telemetryharbor.com)
  * 💬 **Support:** [support@telemetryharbor.com](mailto:support@telemetryharbor.com)
  * 🐛 **Issues:** [GitHub Issues](https://github.com/TelemetryHarbor/harbor-sdk-python/issues)

<!-- end list -->

