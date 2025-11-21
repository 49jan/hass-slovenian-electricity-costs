"""The Slovenian Electricity Costs integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    WEEKDAY_SCHEDULE_HIGHER,
    WEEKDAY_SCHEDULE_LOWER,
    WEEKEND_HOLIDAY_SCHEDULE_HIGHER,
    WEEKEND_HOLIDAY_SCHEDULE_LOWER,
    CONF_ENERGY_VT_PRICE,
    CONF_ENERGY_MT_PRICE,
    CONF_BLOCK_1_PRICE,
    CONF_BLOCK_2_PRICE,
    CONF_BLOCK_3_PRICE,
    CONF_BLOCK_4_PRICE,
    CONF_BLOCK_5_PRICE,
    CONF_CONTRIBUTIONS_PRICE,
    CONF_EXCISE_TAX,
    BLOCK_DESCRIPTIONS,
    ENERGY_DESCRIPTIONS,
    is_holiday,
    get_season,
    get_slovenian_holidays_for_year,
    get_energy_tariff,
    calculate_total_price_per_kwh,
    SEASON_INFO,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Slovenian Electricity Costs from a config entry."""
    
    coordinator = SlovenianElectricityCostsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def update_prices_service(call):
        """Handle update prices service call."""
        data = call.data
        config_data = dict(entry.data)
        
        # Update prices if provided
        for block in range(1, 6):
            price_key = f"block_{block}_price"
            if price_key in data:
                config_data[f"block_{block}_price"] = data[price_key]
        
        # Update config entry
        hass.config_entries.async_update_entry(entry, data=config_data)
        await coordinator.async_request_refresh()

    async def get_current_block_service(call):
        """Handle get current block service call."""
        current_data = coordinator.data
        if current_data:
            current_block = current_data.get("current_block", 3)
            current_total_price = current_data.get("total_price", 0.160000)
            
            # Fire an event with the current block info
            hass.bus.async_fire(f"{DOMAIN}_current_block", {
                "current_block": current_block,
                "total_price": current_total_price,
                "energy_tariff": current_data.get("energy_tariff", "MT"),
                "energy_price": current_data.get("energy_price", 0),
                "network_price": current_data.get("network_price", 0),
                "contributions": current_data.get("contributions", 0),
                "excise_tax": current_data.get("excise_tax", 0),
                "block_description": BLOCK_DESCRIPTIONS.get(current_block, "Unknown"),
                "season": current_data.get("season", "lower"),
                "is_holiday": current_data.get("is_holiday", False),
            })

    async def calculate_cost_service(call):
        """Handle calculate cost service call."""
        consumption = call.data.get("consumption_kwh", 0)
        current_data = coordinator.data
        
        if current_data:
            current_total_price = current_data.get("total_price", 0.160000)
            calculated_cost = consumption * current_total_price
            
            # Fire an event with the calculated cost
            hass.bus.async_fire(f"{DOMAIN}_cost_calculated", {
                "consumption_kwh": consumption,
                "total_price_per_kwh": current_total_price,
                "calculated_cost": calculated_cost,
                "season": current_data.get("season", "lower"),
                "energy_tariff": current_data.get("energy_tariff", "MT"),
            })

    hass.services.async_register(DOMAIN, "update_prices", update_prices_service)
    hass.services.async_register(DOMAIN, "get_current_block", get_current_block_service)
    hass.services.async_register(DOMAIN, "calculate_cost", calculate_cost_service)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Remove services if this is the last integration entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "update_prices")
            hass.services.async_remove(DOMAIN, "get_current_block")
            hass.services.async_remove(DOMAIN, "calculate_cost")

    return unload_ok


class SlovenianElectricityCostsCoordinator(DataUpdateCoordinator):
    """Class to manage electricity cost calculations and data updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.entry = entry
        self.hass = hass

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self._get_current_data()
        except Exception as exception:
            raise UpdateFailed() from exception

    async def _get_current_data(self) -> dict[str, Any]:
        """Get current tariff data."""
        now = datetime.now()
        season = get_season(now)
        is_holiday_today = is_holiday(now)
        
        # Get prices from configuration
        energy_vt_price = self.entry.data.get(CONF_ENERGY_VT_PRICE, 0.1199)
        energy_mt_price = self.entry.data.get(CONF_ENERGY_MT_PRICE, 0.0979)
        
        network_prices = {
            1: self.entry.data.get(CONF_BLOCK_1_PRICE, 0.01998),
            2: self.entry.data.get(CONF_BLOCK_2_PRICE, 0.01833),
            3: self.entry.data.get(CONF_BLOCK_3_PRICE, 0.018090),
            4: self.entry.data.get(CONF_BLOCK_4_PRICE, 0.018550),
            5: self.entry.data.get(CONF_BLOCK_5_PRICE, 0.018730),
        }
        
        contributions = self.entry.data.get(CONF_CONTRIBUTIONS_PRICE, 0.000930)
        excise_tax = self.entry.data.get(CONF_EXCISE_TAX, 0.001530)
        
        # Calculate total pricing
        pricing_info = calculate_total_price_per_kwh(
            now, energy_vt_price, energy_mt_price, network_prices, contributions, excise_tax
        )

        return {
            "current_block": pricing_info["current_block"],
            "energy_tariff": pricing_info["energy_tariff"],
            "energy_price": pricing_info["energy_price"],
            "network_price": pricing_info["network_price"],
            "contributions": pricing_info["contributions"],
            "excise_tax": pricing_info["excise_tax"],
            "total_price": pricing_info["total_price"],
            "network_prices": network_prices,
            "energy_vt_price": energy_vt_price,
            "energy_mt_price": energy_mt_price,
            "block_states": {i: i == pricing_info["current_block"] for i in range(1, 6)},
            "season": season,
            "season_info": SEASON_INFO.get(season, {}),
            "is_holiday": is_holiday_today,
            "holidays_this_year": get_slovenian_holidays_for_year(now.year),
            "last_updated": now.isoformat(),
        }

    def _get_current_tariff_block(self, dt: datetime) -> int:
        """Determine the current tariff block based on date, time, and season."""
        season = get_season(dt)
        is_holiday_today = is_holiday(dt)
        
        # Check if it's a holiday or Sunday
        if is_holiday_today or dt.weekday() == 6:  # Sunday
            if season == "higher":
                schedule = SUNDAY_HOLIDAY_SCHEDULE_HIGHER
            else:
                schedule = SUNDAY_HOLIDAY_SCHEDULE_LOWER
        elif dt.weekday() == 5:  # Saturday
            if season == "higher":
                schedule = SATURDAY_SCHEDULE_HIGHER
            else:
                schedule = SATURDAY_SCHEDULE_LOWER
        else:  # Monday to Friday
            if season == "higher":
                schedule = WEEKDAY_SCHEDULE_HIGHER
            else:
                schedule = WEEKDAY_SCHEDULE_LOWER

        # Get current time in HH:MM format
        current_time = dt.strftime("%H:%M")
        
        # Find the appropriate block
        for slot in schedule:
            start_time = slot["start"]
            end_time = slot["end"]
            
            # Handle midnight crossing
            if end_time == "24:00":
                end_time = "23:59"
            
            if start_time <= current_time <= end_time:
                return slot["block"]
        
        # Fallback to block 3 if no match found
        return 3

    def get_price_for_block(self, block: int) -> float:
        """Get network price for specific block."""
        if self.data is None:
            return 0.0183  # Default network price
        
        return self.data.get("network_prices", {}).get(block, 0.0183)

    def get_current_block(self) -> int:
        """Get current tariff block."""
        if self.data is None:
            return 3  # Default block
        
        return self.data.get("current_block", 3)

    def get_current_total_price(self) -> float:
        """Get current total electricity price (all components)."""
        if self.data is None:
            return 0.160000  # Default total price
        
        return self.data.get("total_price", 0.160000)

    def get_current_season(self) -> str:
        """Get current season."""
        if self.data is None:
            return "lower"
        
        return self.data.get("season", "lower")