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