from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    serial = coordinator.data.get('serial', entry.entry_id)

    sensors = [
        ODISensor(coordinator, entry, "Rx Power", "rx_power", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, serial, 2),
        ODISensor(coordinator, entry, "Tx Power", "tx_power", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, serial, 2),
        ODISensor(coordinator, entry, "Temperature", "temp", "°C", SensorDeviceClass.TEMPERATURE, serial, 1),
        ODISensor(coordinator, entry, "Voltage", "voltage", "V", SensorDeviceClass.VOLTAGE, serial, 3),
        # New Numeric State Sensor
        ODISensor(coordinator, entry, "ONU State Phase", "onu_state_int", None, None, serial, 0),
    ]
    
    binary_sensors = [
        ODIBinarySensor(coordinator, entry, "ONU Status", "onu_state_bool", BinarySensorDeviceClass.CONNECTIVITY, serial)
    ]
    
    async_add_entities(sensors + binary_sensors)

class ODISensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, name, key, unit, device_class, serial, precision):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{serial}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_suggested_display_precision = precision
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
    
    @property
    def extra_state_attributes(self):
        """Add friendly descriptions for the ONU states."""
        # We only want to add these attributes to the numeric phase sensor
        if self._key == "onu_state_int":
            states = {
                1: "Initial State (O1)",
                2: "Standby State (O2)",
                3: "Serial Number State (O3)",
                4: "Ranging State (O4)",
                5: "Operation State (O5)",
                6: "Intermittent State (O6)",
                7: "Emergency Stop (O7)"
            }
            val = self.coordinator.data.get(self._key)
            return {"phase_description": states.get(val, "Unknown")}
        return None

class ODIBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for ONU State (O5)."""
    def __init__(self, coordinator, entry, name, key, device_class, serial):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{serial}_{key}"
        self._attr_device_class = device_class
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
        }

    @property
    def is_on(self):
        """Return true if the ONU is authenticated (O5)."""
        return self.coordinator.data.get("onu_state_bool", False)