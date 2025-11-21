"""Binary sensor platform for Slovenian Electricity Costs integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, BLOCK_DESCRIPTIONS, SEASON_INFO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create binary sensors for each tariff block
    entities = []
    for block in range(1, 6):
        entities.append(TariffBlockBinarySensor(coordinator, config_entry, block))

    # Add season and holiday binary sensors
    entities.append(HigherSeasonBinarySensor(coordinator, config_entry))
    entities.append(HolidayBinarySensor(coordinator, config_entry))
    entities.append(CheapElectricityBinarySensor(coordinator, config_entry))
    entities.append(ExpensiveElectricityBinarySensor(coordinator, config_entry))

    async_add_entities(entities)


class TariffBlockBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for tariff block state."""

    def __init__(self, coordinator, config_entry: ConfigEntry, block: int) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._block = block
        self._attr_unique_id = f"{config_entry.entry_id}_electricity_block_{block}_active"
        self._attr_name = f"Electricity Block {block} Active"
        self._attr_has_entity_name = True
        
        # Set icon based on block
        if block == 1:
            self._attr_icon = "mdi:weather-night"  # Very low rate (night)
        elif block == 2:
            self._attr_icon = "mdi:weather-sunset-down"  # Low rate
        elif block == 3:
            self._attr_icon = "mdi:weather-cloudy"  # Medium rate
        elif block == 4:
            self._attr_icon = "mdi:weather-sunny"  # High rate (peak)
        else:  # block == 5
            self._attr_icon = "mdi:fire"  # Very high rate (special peak)

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Slovenian Electricity Costs",
            "manufacturer": "49jan",
            "model": "Tariff Calculator",
            "sw_version": "1.1-b",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the tariff block is active."""
        if self.coordinator.data is None:
            return None
        
        block_states = self.coordinator.data.get("block_states", {})
        return block_states.get(self._block, False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}

        prices = self.coordinator.data.get("prices", {})
        current_block = self.coordinator.data.get("current_block")
        season = self.coordinator.data.get("season", "lower")
        
        attrs = {
            "block": self._block,
            "description": BLOCK_DESCRIPTIONS.get(self._block, "Unknown"),
            "price": prices.get(self._block, 0),
            "is_current_block": current_block == self._block,
            "season": season,
            "season_name": SEASON_INFO.get(season, {}).get("name", "Unknown"),
            "last_updated": self.coordinator.data.get("last_updated"),
        }
        
        # Add special note for block 5
        if self._block == 5:
            attrs["season_note"] = "Block 5 is only used in higher season (Oct-Mar)"
            
        return attrs


class HigherSeasonBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for higher season status."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_electricity_higher_season"
        self._attr_name = "Electricity Higher Season"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:snowflake"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Slovenian Electricity Costs",
            "manufacturer": "49jan",
            "model": "Tariff Calculator",
            "sw_version": "1.1-b",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if it's higher season."""
        if self.coordinator.data is None:
            return None
        
        season = self.coordinator.data.get("season", "lower")
        return season == "higher"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}

        season = self.coordinator.data.get("season", "lower")
        season_info = SEASON_INFO.get(season, {})
        
        return {
            "season": season,
            "season_name": season_info.get("name", "Unknown"),
            "months": season_info.get("months", "Unknown"),
            "description": season_info.get("description", "Unknown"),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class HolidayBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for holiday status."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_electricity_holiday_today"
        self._attr_name = "Electricity Holiday Today"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:calendar-star"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Slovenian Electricity Costs",
            "manufacturer": "49jan",
            "model": "Tariff Calculator",
            "sw_version": "1.1-b",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if today is a holiday."""
        if self.coordinator.data is None:
            return None
        
        return self.coordinator.data.get("is_holiday", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}
        
        return {
            "holidays_this_year": self.coordinator.data.get("holidays_this_year", []),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class CheapElectricityBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for cheap electricity periods (blocks 1-2)."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_electricity_cheap_rate"
        self._attr_name = "Electricity Cheap Rate"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:currency-eur-off"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Slovenian Electricity Costs",
            "manufacturer": "49jan",
            "model": "Tariff Calculator",
            "sw_version": "1.1-b",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if current tariff is cheap (blocks 1-2)."""
        if self.coordinator.data is None:
            return None
        
        current_block = self.coordinator.data.get("current_block", 3)
        return current_block in [1, 2]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}

        current_block = self.coordinator.data.get("current_block", 3)
        current_price = self.coordinator.data.get("current_price", 0)
        
        return {
            "current_block": current_block,
            "current_price": current_price,
            "cheap_blocks": [1, 2],
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class ExpensiveElectricityBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for expensive electricity periods (blocks 4-5)."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_electricity_expensive_rate"
        self._attr_name = "Electricity Expensive Rate"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:currency-eur"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Slovenian Electricity Costs",
            "manufacturer": "49jan",
            "model": "Tariff Calculator",
            "sw_version": "1.1-b",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if current tariff is expensive (blocks 4-5)."""
        if self.coordinator.data is None:
            return None
        
        current_block = self.coordinator.data.get("current_block", 3)
        return current_block in [4, 5]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}

        current_block = self.coordinator.data.get("current_block", 3)
        current_price = self.coordinator.data.get("current_price", 0)
        
        return {
            "current_block": current_block,
            "current_price": current_price,
            "expensive_blocks": [4, 5],
            "last_updated": self.coordinator.data.get("last_updated"),
        }