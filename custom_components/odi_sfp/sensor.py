from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # We use the serial number from the coordinator as the base for unique IDs
    unique_id = coordinator.data.get('serial', entry.entry_id)

    sensors = [
        ODISensor(coordinator, entry, "Rx Power", "rx_power", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, unique_id),
        ODISensor(coordinator, entry, "Tx Power", "tx_power", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, unique_id),
        ODISensor(coordinator, entry, "Temperature", "temp", "°C", SensorDeviceClass.TEMPERATURE, unique_id),
        ODISensor(coordinator, entry, "Voltage", "voltage", "V", SensorDeviceClass.VOLTAGE, unique_id),
    ]
    
    async_add_entities(sensors)

class ODISensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, name, key, unit, device_class, unique_id_base):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name # No need to put IP in name anymore, the device handles it
        self._attr_unique_id = f"{unique_id_base}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT

        # This links the sensor to the Device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, unique_id_base)},
            "name": f"ODI SFP ({entry.data['host']})",
            "manufacturer": "ODI",
            "model": coordinator.data.get('model', 'DFP-34X-2C2'),
            "sw_version": "Realtek RTL9601D",
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)