import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class ODISFPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ODI xPON SFP."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Create the entry
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
        """Get the options flow for this handler."""
        return ODIOptionsFlowHandler() # No need to pass config_entry here in newer HA versions

class ODIOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update the existing entry with new data
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={**self.config_entry.data, **user_input}
            )
            # We must return an empty dictionary for the options entry
            return self.async_create_entry(title="", data={})

        # Use self.config_entry.data to get current values for the form defaults
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("host", default=self.config_entry.data.get("host")): str,
                vol.Required("username", default=self.config_entry.data.get("username")): str,
                vol.Required("password", default=self.config_entry.data.get("password")): str,
            }),
        )