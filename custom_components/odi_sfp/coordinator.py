import logging
import re
import paramiko
import warnings
from datetime import timedelta
from cryptography.utils import CryptographyDeprecationWarning
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class ODISFPCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        super().__init__(
            hass,
            _LOGGER,
            name=f"ODI SFP {host}",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        return await self.hass.async_add_executor_job(self.fetch_sfp_data)

    def fetch_sfp_data(self):
        warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        results = {}
        try:
            client.connect(
                self.host, 
                username=self.username, 
                password=self.password, 
                timeout=15,
                allow_agent=False,
                look_for_keys=False
            )

 # Define specific search patterns for each command's output
            # This looks for the label and then captures the number following it
            patterns = {
                'rx_power': r"rx\s+power:\s+([-+]?\d*\.\d+|\d+)",
                'tx_power': r"tx\s+power:\s+([-+]?\d*\.\d+|\d+)",
                'temp': r"temperature:\s+([-+]?\d*\.\d+|\d+)",
                'voltage': r"voltage:\s+([-+]?\d*\.\d+|\d+)"
            }

            commands = {
                'rx_power': "diag pon get transceiver rx-power",
                'tx_power': "diag pon get transceiver tx-power",
                'temp': "diag pon get transceiver temperature",
                'voltage': "diag pon get transceiver voltage"
            }

            for key, cmd in commands.items():
                stdin, stdout, stderr = client.exec_command(cmd)
                # We read everything and convert to lowercase for easier matching
                raw_output = stdout.read().decode('utf-8', errors='ignore').lower()
                
                # Use the specific pattern for this key
                match = re.search(patterns[key], raw_output)
                if match:
                    results[key] = float(match.group(1))
                else:
                    _LOGGER.warning(f"Could not parse {key} from output: {raw_output}")
                    results[key] = 0.0

            # ONU State
            stdin, stdout, stderr = client.exec_command("diag gpon get onu-state")
            state_output = stdout.read().decode('utf-8', errors='ignore')
            results['onu_state'] = "O5" in state_output
            
            # Static identifiers from your hardware
            results['serial'] = "PTINA86AD4CF"
            results['model'] = "DFP-34X-2C2/3"

        except Exception as err:
            raise UpdateFailed(f"Error communicating with SFP: {err}")
        finally:
            client.close()
        return results