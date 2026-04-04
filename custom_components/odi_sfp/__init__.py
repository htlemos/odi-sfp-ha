from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import ODISFPCoordinator

async def async_setup_entry(hass: HomeAssistant, entry):
    hass.data.setdefault(DOMAIN, {})
    
    # Pass the entry itself to the coordinator
    coordinator = ODISFPCoordinator(hass, entry)
    
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Listen for updates to the config (like changing the interval)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def update_listener(hass, entry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)