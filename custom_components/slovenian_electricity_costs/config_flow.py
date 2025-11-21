"""Config flow for Slovenian Electricity Costs integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import (
    DOMAIN,
    SUPPLIERS,
    CONF_SUPPLIER,
    CONF_AUTO_UPDATE,
    CONF_CONSUMPTION_SENSOR,
    CONF_ENERGY_VT_PRICE,
    CONF_ENERGY_MT_PRICE,
    CONF_BLOCK_1_PRICE,
    CONF_BLOCK_2_PRICE,
    CONF_BLOCK_3_PRICE,
    CONF_BLOCK_4_PRICE,
    CONF_BLOCK_5_PRICE,
    CONF_CONTRIBUTIONS_PRICE,
    CONF_EXCISE_TAX,
    DEFAULT_PRICES,
    DEFAULT_AUTO_UPDATE,
    BLOCK_DESCRIPTIONS,
    ENERGY_DESCRIPTIONS,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Slovenian Electricity Costs."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._supplier: str | None = None
        self._consumption_sensor: str | None = None
        self._auto_update: bool = DEFAULT_AUTO_UPDATE

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._supplier = user_input[CONF_SUPPLIER]
            self._consumption_sensor = user_input.get(CONF_CONSUMPTION_SENSOR)
            self._auto_update = user_input.get(CONF_AUTO_UPDATE, DEFAULT_AUTO_UPDATE)

            return await self.async_step_prices()

        # Get available energy sensors for consumption
        entity_registry = async_get_entity_registry(self.hass)
        energy_sensors = [
            entity.entity_id
            for entity in entity_registry.entities.values()
            if entity.entity_id.startswith("sensor.")
            and (
                "energy" in entity.entity_id.lower()
                or "consumption" in entity.entity_id.lower()
                or "power" in entity.entity_id.lower()
                or "electricity" in entity.entity_id.lower()
            )
        ]

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SUPPLIER): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": key, "label": value}
                            for key, value in SUPPLIERS.items()
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_CONSUMPTION_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        include_entities=energy_sensors,
                        domain="sensor",
                    )
                ),
                vol.Optional(CONF_AUTO_UPDATE, default=DEFAULT_AUTO_UPDATE): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_prices(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the price configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate prices
            for block in range(1, 6):
                price_key = f"block_{block}_price"
                if user_input.get(price_key, 0) <= 0:
                    errors[price_key] = "invalid_price"

            if not errors:
                # Combine all configuration data
                config_data = {
                    CONF_SUPPLIER: self._supplier,
                    CONF_AUTO_UPDATE: self._auto_update,
                    CONF_ENERGY_VT_PRICE: user_input[CONF_ENERGY_VT_PRICE],
                    CONF_ENERGY_MT_PRICE: user_input[CONF_ENERGY_MT_PRICE],
                    CONF_BLOCK_1_PRICE: user_input[CONF_BLOCK_1_PRICE],
                    CONF_BLOCK_2_PRICE: user_input[CONF_BLOCK_2_PRICE],
                    CONF_BLOCK_3_PRICE: user_input[CONF_BLOCK_3_PRICE],
                    CONF_BLOCK_4_PRICE: user_input[CONF_BLOCK_4_PRICE],
                    CONF_BLOCK_5_PRICE: user_input[CONF_BLOCK_5_PRICE],
                    CONF_CONTRIBUTIONS_PRICE: user_input[CONF_CONTRIBUTIONS_PRICE],
                    CONF_EXCISE_TAX: user_input[CONF_EXCISE_TAX],
                }

                if self._consumption_sensor:
                    config_data[CONF_CONSUMPTION_SENSOR] = self._consumption_sensor

                # Create unique entry ID based on supplier
                unique_id = f"{DOMAIN}_{self._supplier}"
                await self.async_set_unique_id(unique_id)

                return self.async_create_entry(
                    title=f"Slovenian Electricity Costs - {SUPPLIERS[self._supplier]}",
                    data=config_data,
                )

        # Price configuration schema with all components
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ENERGY_VT_PRICE,
                    default=DEFAULT_PRICES[CONF_ENERGY_VT_PRICE],
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Required(
                    CONF_ENERGY_MT_PRICE,
                    default=DEFAULT_PRICES[CONF_ENERGY_MT_PRICE],
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Required(
                    CONF_BLOCK_1_PRICE,
                    default=DEFAULT_PRICES[CONF_BLOCK_1_PRICE],
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Required(
                    CONF_BLOCK_2_PRICE,
                    default=DEFAULT_PRICES[CONF_BLOCK_2_PRICE],
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Required(
                    CONF_BLOCK_3_PRICE,
                    default=DEFAULT_PRICES[CONF_BLOCK_3_PRICE],
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Required(
                    CONF_BLOCK_4_PRICE,
                    default=DEFAULT_PRICES[CONF_BLOCK_4_PRICE],
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Required(
                    CONF_BLOCK_5_PRICE,
                    default=DEFAULT_PRICES[CONF_BLOCK_5_PRICE],
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Required(
                    CONF_CONTRIBUTIONS_PRICE,
                    default=DEFAULT_PRICES[CONF_CONTRIBUTIONS_PRICE],
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Required(
                    CONF_EXCISE_TAX,
                    default=DEFAULT_PRICES[CONF_EXCISE_TAX],
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
            }
        )

        return self.async_show_form(
            step_id="prices",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "supplier": SUPPLIERS.get(self._supplier, "Unknown"),
                "energy_vt_desc": ENERGY_DESCRIPTIONS["VT"],
                "energy_mt_desc": ENERGY_DESCRIPTIONS["MT"],
                "block_1_desc": BLOCK_DESCRIPTIONS[1],
                "block_2_desc": BLOCK_DESCRIPTIONS[2],
                "block_3_desc": BLOCK_DESCRIPTIONS[3],
                "block_4_desc": BLOCK_DESCRIPTIONS[4],
                "block_5_desc": BLOCK_DESCRIPTIONS[5],
                "contributions_info": "Prispevki (RES, OVES, EKO sklad, itd.)",
                "excise_info": "Trošarina na električno energijo",
            },
        )


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Slovenian Electricity Costs."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_AUTO_UPDATE,
                    default=self.config_entry.data.get(CONF_AUTO_UPDATE, DEFAULT_AUTO_UPDATE),
                ): bool,
                vol.Optional(
                    CONF_BLOCK_1_PRICE,
                    default=self.config_entry.data.get(CONF_BLOCK_1_PRICE, DEFAULT_PRICES[CONF_BLOCK_1_PRICE]),
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Optional(
                    CONF_BLOCK_2_PRICE,
                    default=self.config_entry.data.get(CONF_BLOCK_2_PRICE, DEFAULT_PRICES[CONF_BLOCK_2_PRICE]),
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Optional(
                    CONF_BLOCK_3_PRICE,
                    default=self.config_entry.data.get(CONF_BLOCK_3_PRICE, DEFAULT_PRICES[CONF_BLOCK_3_PRICE]),
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Optional(
                    CONF_BLOCK_4_PRICE,
                    default=self.config_entry.data.get(CONF_BLOCK_4_PRICE, DEFAULT_PRICES[CONF_BLOCK_4_PRICE]),
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
                vol.Optional(
                    CONF_BLOCK_5_PRICE,
                    default=self.config_entry.data.get(CONF_BLOCK_5_PRICE, DEFAULT_PRICES[CONF_BLOCK_5_PRICE]),
                    description={"suffix": "€/kWh"},
                ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )