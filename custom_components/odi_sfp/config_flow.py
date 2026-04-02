from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ODISFPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # You could add a validation check here to test SSH connection
            return self.async_create_entry(title=f"ODI SFP ({user_input['host']})", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default="192.168.1.1"): str,
                vol.Required("username", default="admin"): str,
                vol.Required("password", default="admin"): str,
            }),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return ODIOptionsFlowHandler(config_entry)

class ODIOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # This updates the actual ConfigEntry data
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={**self.config_entry.data, **user_input}
            )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("host", default=self.config_entry.data.get("host")): str,
                vol.Required("username", default=self.config_entry.data.get("username")): str,
                vol.Required("password", default=self.config_entry.data.get("password")): str,
            }),
        )