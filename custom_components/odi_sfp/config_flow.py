import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

# Set a sensible default (e.g., 60 seconds)
DEFAULT_INTERVAL = 60

class ODISFPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=f"ODI SFP ({user_input['host']})", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default="192.168.1.1"): str,
                vol.Required("username", default="admin"): str,
                vol.Required("password", default="admin"): str,
                vol.Required("update_interval", default=DEFAULT_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=10, max=3600)
                ),
            }),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return ODIOptionsFlowHandler()

class ODIOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={**self.config_entry.data, **user_input}
            )
            # This triggers a reload of the integration to apply the new interval
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("host", default=self.config_entry.data.get("host")): str,
                vol.Required("username", default=self.config_entry.data.get("username")): str,
                vol.Required("password", default=self.config_entry.data.get("password")): str,
                vol.Required(
                    "update_interval", 
                    default=self.config_entry.data.get("update_interval", DEFAULT_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
            }),
        )