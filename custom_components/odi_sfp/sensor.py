from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Define your sensors here
    sensors = [
        ODISensor(coordinator, entry, "Rx Power", "rx_power", "dBm", SensorDeviceClass.SIGNAL_STRENGTH),
        ODISensor(coordinator, entry, "Tx Power", "tx_power", "dBm", SensorDeviceClass.SIGNAL_STRENGTH),
        ODISensor(coordinator, entry, "Temperature", "temp", "°C", SensorDeviceClass.TEMPERATURE),
        ODISensor(coordinator, entry, "Voltage", "voltage", "V", SensorDeviceClass.VOLTAGE),
    ]
    
    async_add_entities(sensors)

class ODISensor(CoordinatorEntity, SensorEntity):
    """Representation of an ODI SFP sensor."""
    def __init__(self, coordinator, entry, name, key, unit, device_class):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"ODI {name} ({entry.data['host']})"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._key)