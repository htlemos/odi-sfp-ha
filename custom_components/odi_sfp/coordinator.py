import logging
import re
import asyncio
import paramiko
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class ODISFPCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the ODI SFP stick."""

    def __init__(self, hass, host, username, password):
        """Initialize."""
        self.host = host
        self.username = username
        self.password = password
        
        super().__init__(
            hass,
            _LOGGER,
            name="ODI SFP Statistics",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        """Fetch data from the SFP stick."""
        return await self.hass.async_add_executor_job(self.fetch_sfp_data)

    def fetch_sfp_data(self):
        """Actual SSH logic to pull data from the ODI SFP stick."""
        import warnings
        import paramiko
        import re
        from cryptography.utils import CryptographyDeprecationWarning
        
        # Suppress TripleDES warnings for Python 3.14 compatibility
        warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        results = {}
        try:
            # Establish connection
            client.connect(
                self.host, 
                username=self.username, 
                password=self.password, 
                timeout=15,
                allow_agent=False,
                look_for_keys=False,
                # Compatibility for older Realtek firmware SSH handshakes
                disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
            )
            
            # 1. Get Device Info (Serial Number)
            stdin, stdout, stderr = client.exec_command("diag gpon get sn")
            sn_raw = stdout.read().decode('utf-8')
            # Look for SN: followed by alphanumeric characters
            sn_match = re.search(r"SN:\s+([A-Za-z0-9]+)", sn_raw)
            results['serial'] = sn_match.group(1) if sn_match else f"ODI_{self.host.replace('.', '')}"

            # 2. Get Model/Firmware Info
            stdin, stdout, stderr = client.exec_command("cat /etc/version")
            results['model'] = stdout.read().decode('utf-8').strip() or "DFP-34X-2C2"

            # 3. Get Optical Stats
            stdin, stdout, stderr = client.exec_command("diag optic get all")
            optic_output = stdout.read().decode('utf-8')
            
            # 4. Get ONU State (O5 means authenticated/up)
            stdin, stdout, stderr = client.exec_command("diag gpon get onu-state")
            state_output = stdout.read().decode('utf-8')

            # Regex Parsing for sensors
            results['rx_power'] = self._parse_value(r"Rx Power:\s+([-+]?\d*\.\d+|\d+)", optic_output)
            results['tx_power'] = self._parse_value(r"Tx Power:\s+([-+]?\d*\.\d+|\d+)", optic_output)
            results['temp'] = self._parse_value(r"Temperature:\s+([-+]?\d*\.\d+|\d+)", optic_output)
            results['voltage'] = self._parse_value(r"Voltage:\s+([-+]?\d*\.\d+|\d+)", optic_output)
            
            # Boolean for binary sensor: True if O5 is found in the output
            results['onu_state'] = "O5" in state_output

        except Exception as err:
            _LOGGER.error(f"SSH Connection to ODI SFP ({self.host}) failed: {err}")
            raise UpdateFailed(f"Error communicating with SFP: {err}")
        finally:
            client.close()
            
        return results

    def _parse_value(self, pattern, text):
        """Helper to safely extract float values from shell output."""
        match = re.search(pattern, text)
        try:
            return float(match.group(1)) if match else None
        except (ValueError, IndexError):
            return None

    def _parse_value(self, pattern, text):
        """Helper to extract numbers from shell output."""
        match = re.search(pattern, text)
        return float(match.group(1)) if match else None