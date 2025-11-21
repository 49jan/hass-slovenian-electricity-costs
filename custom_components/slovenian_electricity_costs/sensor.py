"""Sensor platform for Slovenian Electricity Costs integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers import entity_registry as er

from .const import (
    DOMAIN,
    CONF_CONSUMPTION_SENSOR,
    BLOCK_DESCRIPTIONS,
    ENERGY_DESCRIPTIONS,
    SEASON_INFO,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Create all sensors
    entities = []

    # Current tariff block sensor
    entities.append(CurrentTariffBlockSensor(coordinator, config_entry))

    # Current electricity price sensor (total)
    entities.append(CurrentElectricityPriceSensor(coordinator, config_entry))

    # Energy tariff sensor (VT/MT)
    entities.append(EnergyTariffSensor(coordinator, config_entry))

    # Individual component sensors
    entities.append(EnergyPriceSensor(coordinator, config_entry))
    entities.append(NetworkPriceSensor(coordinator, config_entry))
    entities.append(ContributionsPriceSensor(coordinator, config_entry))
    entities.append(ExciseTaxSensor(coordinator, config_entry))

    # Current season sensor
    entities.append(CurrentSeasonSensor(coordinator, config_entry))

    # Holiday status sensor
    entities.append(HolidayStatusSensor(coordinator, config_entry))

    # Electricity cost sensor (if consumption sensor is configured)
    consumption_sensor = config_entry.data.get(CONF_CONSUMPTION_SENSOR)
    if consumption_sensor:
        entities.append(ElectricityCostSensor(coordinator, config_entry, consumption_sensor))

    # Individual price sensors for each network block
    for block in range(1, 6):
        entities.append(NetworkBlockPriceSensor(coordinator, config_entry, block))

    async_add_entities(entities)


class SlovenianElectricityCostsSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Slovenian Electricity Costs sensors."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Slovenian Electricity Costs",
            "manufacturer": "byJan",
            "model": "Tariff Calculator",
            "sw_version": "1.0.0",
        }


class CurrentTariffBlockSensor(SlovenianElectricityCostsSensorBase):
    """Sensor for current tariff block."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_current_block"
        self._attr_name = "Current Tariff Block"
        self._attr_icon = "mdi:clock-time-four"

    @property
    def native_value(self) -> int | None:
        """Return the current tariff block."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("current_block")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}
        
        current_block = self.coordinator.data.get("current_block")
        season = self.coordinator.data.get("season", "lower")
        
        return {
            "block_description": BLOCK_DESCRIPTIONS.get(current_block, "Unknown"),
            "season": season,
            "season_name": SEASON_INFO.get(season, {}).get("name", "Unknown"),
            "is_holiday": self.coordinator.data.get("is_holiday", False),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class CurrentElectricityPriceSensor(SlovenianElectricityCostsSensorBase):
    """Sensor for current total electricity price (all components)."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_current_total_price"
        self._attr_name = "Current Total Electricity Price"
        self._attr_icon = "mdi:currency-eur"
        self._attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the current total electricity price."""
        if self.coordinator.data is None:
            return None
        return round(self.coordinator.data.get("total_price", 0), 6)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}
        
        current_block = self.coordinator.data.get("current_block")
        season = self.coordinator.data.get("season", "lower")
        energy_tariff = self.coordinator.data.get("energy_tariff", "MT")
        
        return {
            "energy_tariff": energy_tariff,
            "energy_price": self.coordinator.data.get("energy_price", 0),
            "current_block": current_block,
            "network_price": self.coordinator.data.get("network_price", 0),
            "contributions": self.coordinator.data.get("contributions", 0),
            "excise_tax": self.coordinator.data.get("excise_tax", 0),
            "season": season,
            "season_name": SEASON_INFO.get(season, {}).get("name", "Unknown"),
            "is_holiday": self.coordinator.data.get("is_holiday", False),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class CurrentSeasonSensor(SlovenianElectricityCostsSensorBase):
    """Sensor for current electricity season."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_current_season"
        self._attr_name = "Current Season"
        self._attr_icon = "mdi:calendar-range"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        """Return the current season."""
        if self.coordinator.data is None:
            return None
        
        season = self.coordinator.data.get("season", "lower")
        return SEASON_INFO.get(season, {}).get("name", "Unknown")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}
        
        season = self.coordinator.data.get("season", "lower")
        season_info = SEASON_INFO.get(season, {})
        
        return {
            "season_code": season,
            "months": season_info.get("months", "Unknown"),
            "description": season_info.get("description", "Unknown"),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class HolidayStatusSensor(SlovenianElectricityCostsSensorBase):
    """Sensor for holiday status."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{config_entry.entry_id}_holiday_status"
        self._attr_name = "Holiday Status"
        self._attr_icon = "mdi:calendar-star"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        """Return the holiday status."""
        if self.coordinator.data is None:
            return None
        
        is_holiday = self.coordinator.data.get("is_holiday", False)
        return "Holiday" if is_holiday else "Working Day"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}
        
        return {
            "is_holiday": self.coordinator.data.get("is_holiday", False),
            "holidays_this_year": self.coordinator.data.get("holidays_this_year", []),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class ElectricityCostSensor(SlovenianElectricityCostsSensorBase):
    """Sensor for electricity cost calculation."""

    def __init__(self, coordinator, config_entry: ConfigEntry, consumption_sensor: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._consumption_sensor = consumption_sensor
        self._attr_unique_id = f"{config_entry.entry_id}_electricity_cost"
        self._attr_name = "Electricity Cost"
        self._attr_icon = "mdi:cash"
        self._attr_native_unit_of_measurement = CURRENCY_EURO
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float | None:
        """Return the calculated electricity cost."""
        if self.coordinator.data is None:
            return None

        # Get consumption from the configured sensor
        consumption_state = self.hass.states.get(self._consumption_sensor)
        if consumption_state is None or consumption_state.state == "unavailable":
            return None

        try:
            consumption = float(consumption_state.state)
            current_price = self.coordinator.data.get("current_price", 0)
            return round(consumption * current_price, 2)
        except (ValueError, TypeError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return {}

        consumption_state = self.hass.states.get(self._consumption_sensor)
        consumption = 0
        if consumption_state and consumption_state.state != "unavailable":
            try:
                consumption = float(consumption_state.state)
            except (ValueError, TypeError):
                consumption = 0

        current_block = self.coordinator.data.get("current_block")
        current_price = self.coordinator.data.get("current_price", 0)
        season = self.coordinator.data.get("season", "lower")

        return {
            "consumption_kwh": consumption,
            "current_price": current_price,
            "current_block": current_block,
            "block_description": BLOCK_DESCRIPTIONS.get(current_block, "Unknown"),
            "season": season,
            "season_name": SEASON_INFO.get(season, {}).get("name", "Unknown"),
            "is_holiday": self.coordinator.data.get("is_holiday", False),
            "consumption_sensor": self._consumption_sensor,
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class TariffBlockPriceSensor(SlovenianElectricityCostsSensorBase):
    """Sensor for individual tariff block prices."""

    def __init__(self, coordinator, config_entry: ConfigEntry, block: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._block = block
        self._attr_unique_id = f"{config_entry.entry_id}_block_{block}_price"
        self._attr_name = f"Block {block} Price"
        self._attr_icon = "mdi:currency-eur"
        self._attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        """Return the price for this tariff block."""
        if self.coordinator.data is None:
            return None
        
        prices = self.coordinator.data.get("prices", {})
        return round(prices.get(self._block, 0), 6)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        season = "lower"
        if self.coordinator.data:
            season = self.coordinator.data.get("season", "lower")
            
        attrs = {
            "block": self._block,
            "description": BLOCK_DESCRIPTIONS.get(self._block, "Unknown"),
            "season": season,
        }
        
        # Add special note for block 5
        if self._block == 5:
            attrs["season_note"] = "Block 5 is only used in higher season (Oct-Mar)"
            
        return attrs