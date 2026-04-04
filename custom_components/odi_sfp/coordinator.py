import logging
import re
import paramiko
import warnings
from datetime import timedelta
from cryptography.utils import CryptographyDeprecationWarning
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class ODISFPCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.host = entry.data["host"]
        self.username = entry.data["username"]
        self.password = entry.data["password"]
        
        # CPU tracking variables for delta calculation
        self._last_total_ticks = None
        self._last_idle_ticks = None

        # Interval comes from user configuration
        scan_interval = entry.data.get("update_interval", 60)

        super().__init__(
            hass,
            _LOGGER,
            name=f"ODI SFP {self.host}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        return await self.hass.async_add_executor_job(self.fetch_sfp_data)

    def fetch_sfp_data(self):
        warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        results = {}
        try:
            client.connect(self.host, username=self.username, password=self.password, timeout=15)

            # Combined batch command for efficiency
            all_cmds = (
                "diag pon get transceiver rx-power; "
                "diag pon get transceiver tx-power; "
                "diag pon get transceiver bias-current; "
                "diag pon get transceiver temperature; "
                "diag pon get transceiver voltage; "
                "diag gpon get onu-state; "
                "cat /proc/uptime; "
                "cat /proc/meminfo; "
                "cat /proc/stat"
            )

            stdin, stdout, stderr = client.exec_command(all_cmds)
            raw_output = stdout.read().decode('utf-8', errors='ignore')

            def extract(pattern, text, index=1):
                match = re.search(pattern, text, re.IGNORECASE)
                return match.group(index) if match else None

            # --- Optical & Health ---
            results['rx_power'] = float(extract(r"Rx Power[:\s]+([-+]?\d*\.\d+|\d+)", raw_output) or 0)
            results['tx_power'] = float(extract(r"Tx Power[:\s]+([-+]?\d*\.\d+|\d+)", raw_output) or 0)
            results['bias_current'] = float(extract(r"Bias Current[:\s]+([-+]?\d*\.\d+|\d+)", raw_output) or 0)
            results['temp'] = float(extract(r"Temperature[:\s]+([-+]?\d*\.\d+|\d+)", raw_output) or 0)
            results['voltage'] = float(extract(r"Voltage[:\s]+([-+]?\d*\.\d+|\d+)", raw_output) or 0)
            
            # --- ONU State ---
            state_val = extract(r"O([1-7])", raw_output)
            results['onu_state_int'] = int(state_val) if state_val else 0
            results['onu_state_bool'] = (results['onu_state_int'] == 5)

            # --- System Stats ---
            # We look for two floats separated by a space on their own line
            # Example: 339289.09 335181.35
            uptime_match = re.search(r"(\d+\.\d+)\s+\d+\.\d+", raw_output)
            if uptime_match:
                total_seconds = float(uptime_match.group(1))
                # Convert to hours: 339289 / 3600 = 94.2
                results['uptime'] = round(total_seconds / 3600, 1)
            else:
                # Fallback: just find the first number that looks like a large uptime
                # specifically avoiding the small numbers like '3.24' from voltage
                uptime_fallback = re.findall(r"(\d{5,}\.\d+)", raw_output)
                if uptime_fallback:
                    results['uptime'] = round(float(uptime_fallback[-1]) / 3600, 1)
                else:
                    results['uptime'] = 0.0

            mem_val = extract(r"MemFree[:\s]+(\d+)", raw_output)
            results['mem_free'] = round(int(mem_val) / 1024, 2) if mem_val else 0

            # --- CPU Calculation (Deltas) ---
            cpu_match = re.search(r"cpu\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", raw_output)
            if cpu_match:
                ticks = [int(x) for x in cpu_match.groups()]
                total_ticks = sum(ticks)
                idle_ticks = ticks[3]

                if self._last_total_ticks is not None:
                    diff_total = total_ticks - self._last_total_ticks
                    diff_idle = idle_ticks - self._last_idle_ticks
                    if diff_total > 0:
                        usage = 100 * (1 - (diff_idle / diff_total))
                        results['cpu_usage'] = round(max(0, min(100, usage)), 1)
                    else:
                        results['cpu_usage'] = 0.0
                else:
                    results['cpu_usage'] = 0.0

                self._last_total_ticks = total_ticks
                self._last_idle_ticks = idle_ticks

            # Identifiers
            results['serial'] = "PTINA86AD4CF"
            results['model'] = "DFP-34X-2C2/3"

        except Exception as err:
            raise UpdateFailed(f"SSH Communication Error: {err}")
        finally:
            client.close()
        return results