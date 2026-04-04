# ODI xPON SFP Integration for Home Assistant

A custom integration for Home Assistant to monitor optical statistics, connection states, and hardware health from **ODI DFP-34X-2C2/3** (Realtek RTL9601D based) xPON SFP sticks via SSH.

*Co-piloted by Gemini AI 🤖*

## 🚀 Features
- **Grouped Device:** All entities are automatically grouped under a single "ODI SFP" device based on the hardware serial number.
- **Optical Monitoring:** High-precision monitoring of Rx/Tx Power and Laser Bias Current.
- **System Health:** Tracks CPU Average Usage (via tick deltas), Memory Free, and Uptime.
- **Connection Handshake:** Tracks the GPON registration state (O1-O7) with friendly text descriptions provided via attributes.
- **UI Configuration:** Setup and modify IP, Credentials, and **Polling Interval** directly from the Integrations UI.
- **Resource Efficient:** Uses a single SSH session and a semicolon-batch command to minimize CPU spikes on the SFP stick.

## 📊 Entities
| Entity | Class | Description |
| :--- | :--- | :--- |
| **ONU Status** | Connectivity | `On` when in O5 (Operation State). |
| **Rx Power** | Signal Strength | Optical receive level from ISP (dBm). |
| **Tx Power** | Signal Strength | Optical transmit level (dBm). |
| **Bias Current** | Current | Laser diode drive current (mA). Monitor for hardware aging. |
| **Temperature** | Temperature | Internal SFP temperature (°C). |
| **Voltage** | Voltage | Internal supply voltage (V). |
| **CPU Usage** | Power | Average CPU load (%) calculated between polling intervals. |
| **Memory Free** | Data | Available RAM (MB). |
| **Uptime** | Duration | Total system uptime in hours (h). |
| **ONU State Phase** | Numeric | Current GPON state (1-7). Descriptive text in attributes. |

## 🛠 Installation

### Manual Installation
1. Copy the `odi_sfp` folder to your `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration**.
4. Search for **ODI xPON SFP** and enter your SFP stick's IP, username, password, and desired polling interval (default 60s).

## ⚠️ Requirements
- SFP Stick with SSH enabled (usually port 22).
- Default credentials are often `admin` / `admin`.
- **Note:** Polling faster than 30 seconds is not recommended due to the high CPU overhead of SSH encryption on the Realtek chip.

## 🎨 Custom Dashboard Layout

This layout provides a professional "NOC" style view with side-by-side gauges for Signal and CPU health.

```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: gauge
        entity: sensor.odi_sfp_192_168_1_1_rx_power
        name: Fiber Signal (Rx)
        min: -30
        max: -5
        severity:
          green: -24
          yellow: -27
          red: -30
        needle: true
      - type: gauge
        entity: sensor.odi_sfp_192_168_1_1_cpu_usage
        name: CPU Load
        min: 0
        max: 100
        severity:
          green: 0
          yellow: 60
          red: 85
        needle: true
  - type: entities
    title: ODI SFP Diagnostics
    show_header_toggle: false
    entities:
      - entity: sensor.odi_sfp_192_168_1_1_onu_status
        name: Link Status
        icon: mdi:router-wireless
      - entity: sensor.odi_sfp_192_168_1_1_onu_state_phase
        name: Registration Detail
        type: attribute
        attribute: phase_description
        icon: mdi:information-outline
      - type: divider
      - entity: sensor.odi_sfp_192_168_1_1_bias_current
        name: Laser Bias Current
        icon: mdi:current-dc
      - entity: sensor.odi_sfp_192_168_1_1_tx_power
        name: Transmit Power
      - type: divider
      - entity: sensor.odi_sfp_192_168_1_1_temperature
        name: Internal Temp
      - entity: sensor.odi_sfp_192_168_1_1_voltage
        name: Supply Voltage
      - entity: sensor.odi_sfp_192_168_1_1_memory_free
        name: Memory Available
        icon: mdi:memory
      - entity: sensor.odi_sfp_192_168_1_1_uptime
        name: Stick Uptime
        icon: mdi:clock-outline