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
        """Actual SSH logic to pull data."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        results = {}
        try:
            # We use a short timeout because the stick's CPU is weak
            client.connect(
                self.host, 
                username=self.username, 
                password=self.password, 
                timeout=15,
                allow_agent=False,
                look_for_keys=False
            )
            
            # Command 1: Optical Stats
            stdin, stdout, stderr = client.exec_command("diag optic get all")
            optic_output = stdout.read().decode('utf-8')
            
            # Command 2: ONU State
            stdin, stdout, stderr = client.exec_command("diag gpon get onu-state")
            state_output = stdout.read().decode('utf-8')

            # Regex Parsing - Matches "Rx Power: -18.23 dBm" or "Temperature: 52.4 C"
            results['rx_power'] = self._parse_value(r"Rx Power:\s+([-+]?\d*\.\d+|\d+)", optic_output)
            results['tx_power'] = self._parse_value(r"Tx Power:\s+([-+]?\d*\.\d+|\d+)", optic_output)
            results['temp'] = self._parse_value(r"Temperature:\s+([-+]?\d*\.\d+|\d+)", optic_output)
            results['voltage'] = self._parse_value(r"Voltage:\s+([-+]?\d*\.\d+|\d+)", optic_output)
            
            # State Check (O5 is the 'Up' state for GPON)
            results['onu_state'] = "O5" in state_output

        except Exception as err:
            _LOGGER.error(f"SSH Connection to ODI SFP failed: {err}")
            raise UpdateFailed(f"Error communicating with SFP: {err}")
        finally:
            client.close()
            
        return results

    def _parse_value(self, pattern, text):
        """Helper to extract numbers from shell output."""
        match = re.search(pattern, text)
        return float(match.group(1)) if match else None