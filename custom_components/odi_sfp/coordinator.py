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
        """Fetch all data in a single SSH session to reduce CPU load on the stick."""
        import warnings
        import paramiko
        import re
        from cryptography.utils import CryptographyDeprecationWarning
        
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

            # Combine all commands into one string separated by semicolons
            # This is much faster and more stable for the SFP stick
            all_cmds = (
                "diag pon get transceiver rx-power; "
                "diag pon get transceiver tx-power; "
                "diag pon get transceiver temperature; "
                "diag pon get transceiver voltage; "
                "diag gpon get onu-state"
            )

            stdin, stdout, stderr = client.exec_command(all_cmds)
            # Read the entire output at once
            raw_output = stdout.read().decode('utf-8', errors='ignore')
            _LOGGER.debug(f"ODI Raw Output: {raw_output}")

            # Strict Regex Parsing
            # We look for the Label (case insensitive) and the number immediately following
            def extract(label, text):
                # Matches "Rx Power: -21.73" or "Temperature: 45.7"
                match = re.search(rf"{label}[:\s]+([-+]?\d*\.\d+|\d+)", text, re.IGNORECASE)
                return float(match.group(1)) if match else 0.0

            results['rx_power'] = extract("Rx Power", raw_output)
            results['tx_power'] = extract("Tx Power", raw_output)
            results['temp'] = extract("Temperature", raw_output)
            results['voltage'] = extract("Voltage", raw_output)
            
            # ONU State check
            results['onu_state'] = "O5" in raw_output

            # Search for the ONU state pattern (O followed by a digit)
            # Typical output: "ONU State: O5"
            state_match = re.search(r"O([1-7])", raw_output)
            if state_match:
                state_val = int(state_match.group(1))
                results['onu_state_int'] = state_val
                results['onu_state_bool'] = (state_val == 5)
            else:
                results['onu_state_int'] = 0
                results['onu_state_bool'] = False
            
            # Identifiers
            results['serial'] = "PTINA86AD4CF"
            results['model'] = "DFP-34X-2C2/3"

        except Exception as err:
            _LOGGER.error(f"SSH Error polling ODI SFP: {err}")
            raise UpdateFailed(err)
        finally:
            client.close()
            
        return results