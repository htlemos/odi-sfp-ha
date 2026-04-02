from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import ODISFPCoordinator # Assuming you put the class in coordinator.py

async def async_setup_entry(hass: HomeAssistant, entry):
    hass.data.setdefault(DOMAIN, {})
    
    coordinator = ODISFPCoordinator(
        hass, 
        entry.data["host"], 
        entry.data["username"], 
        entry.data["password"]
    )
    
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok