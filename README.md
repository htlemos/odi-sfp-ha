# ODI xPON SFP Integration for Home Assistant

A custom integration for Home Assistant to monitor optical statistics and connection states from ODI DFP-34X-2C2/3 (Realtek RTL9601D based) xPON SFP sticks via SSH.

*Co-piloted by Gemini AI 🤖*

## Features
- **Grouped Device:** All entities are automatically grouped under a single "ODI SFP" device.
- **Optical Monitoring:** High-precision monitoring of Rx/Tx Power, Temperature, and Voltage.
- **Connection Handshake:** Tracks the GPON registration state (O1-O7) with friendly descriptions.
- **UI Configuration:** Setup and modify IP/Credentials directly from the Home Assistant Integrations UI.
- **Resource Efficient:** Uses a single SSH session per update cycle to minimize load on the SFP stick's CPU.

## Entities
| Entity | Class | Description |
| :--- | :--- | :--- |
| **ONU Status** | Connectivity | `On` when in O5 (Operation State) |
| **Rx Power** | Signal Strength | Optical receive level from ISP (dBm) |
| **Tx Power** | Signal Strength | Optical transmit level (dBm) |
| **Temperature** | Temperature | Internal SFP temperature (°C) |
| **Voltage** | Voltage | Internal supply voltage (V) |
| **ONU State Phase** | Numeric | Current GPON state (1-7) |

## Installation

### Manual Installation
1. Copy the `odi_sfp` folder to your `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration**.
4. Search for **ODI xPON SFP** and enter your SFP stick's IP, username, and password.

## Requirements
- SFP Stick with SSH enabled (usually port 22).
- Default credentials are often `admin` / `admin`.

## Credits
Based on the Realtek diagnostic shell (`RTK.0>`) commands found in various community research projects (Anime4000/RTL960x).

---
*Disclaimer: Use this integration at your own risk. Frequent polling of low-power SFP sticks can occasionally cause reboots on certain firmware versions.*

---

## 🎨 Custom Dashboard layout

```yaml
type: vertical-stack
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
  - type: entities
    title: ODI SFP Handshake
    show_header_toggle: false
    entities:
      - entity: sensor.odi_sfp_192_168_1_1_onu_status
        name: Link Status
      - entity: sensor.odi_sfp_192_168_1_1_onu_state_phase
        name: Handshake Phase
      - entity: sensor.odi_sfp_192_168_1_1_onu_state_phase
        name: Registration Detail
        type: attribute
        attribute: phase_description
        icon: mdi:information-outline
      - type: divider
      - entity: sensor.odi_sfp_192_168_1_1_temperature
        name: Stick Temp
      - entity: sensor.odi_sfp_192_168_1_1_voltage
        name: Internal Voltage
      - entity: sensor.odi_sfp_192_168_1_1_tx_power
        name: Transmit Power
