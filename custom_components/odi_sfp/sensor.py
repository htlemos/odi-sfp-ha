from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    serial = coordinator.data.get('serial', entry.entry_id)

    sensors = [
        ODISensor(coordinator, entry, "Rx Power", "rx_power", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, serial),
        ODISensor(coordinator, entry, "Tx Power", "tx_power", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, serial),
        ODISensor(coordinator, entry, "Temperature", "temp", "°C", SensorDeviceClass.TEMPERATURE, serial),
        ODISensor(coordinator, entry, "Voltage", "voltage", "V", SensorDeviceClass.VOLTAGE, serial),
    ]
    async_add_entities(sensors)

class ODISensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, name, key, unit, device_class, serial):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{serial}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": f"ODI SFP ({entry.data['host']})",
            "manufacturer": "ODI",
            "model": coordinator.data.get('model'),
            "sw_version": "V1.0-220923",
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)