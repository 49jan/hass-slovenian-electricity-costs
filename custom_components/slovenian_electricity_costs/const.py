"""Constants for the Slovenian Electricity Costs integration."""
from datetime import date, datetime, timedelta
from typing import Dict, List

DOMAIN = "slovenian_electricity_costs"

# Configuration keys
CONF_SUPPLIER = "supplier"
CONF_AUTO_UPDATE = "auto_update"
CONF_CONSUMPTION_SENSOR = "consumption_sensor"

# Energy pricing components
CONF_ENERGY_VT_PRICE = "energy_vt_price"  # Električna energija VT
CONF_ENERGY_MT_PRICE = "energy_mt_price"  # Električna energija MT
CONF_BLOCK_1_PRICE = "block_1_price"      # Omrežnina blok 1
CONF_BLOCK_2_PRICE = "block_2_price"      # Omrežnina blok 2
CONF_BLOCK_3_PRICE = "block_3_price"      # Omrežnina blok 3
CONF_BLOCK_4_PRICE = "block_4_price"      # Omrežnina blok 4
CONF_BLOCK_5_PRICE = "block_5_price"      # Omrežnina blok 5
CONF_CONTRIBUTIONS_PRICE = "contributions_price"  # Prispevki (RES, OVES, itd.)
CONF_EXCISE_TAX = "excise_tax"             # Trošarina

# Default values
DEFAULT_SCAN_INTERVAL = 60  # seconds
DEFAULT_AUTO_UPDATE = False

# Slovenian electricity suppliers (dobavitelji) and distributors
SUPPLIERS = {
    "gen_i": "GEN-I",
    "petrol": "Petrol",
    "elektro_energija": "Elektro energija",
    "eco_energy": "ECO energy",
    "elektro_ljubljana": "Elektro Ljubljana (osnovni dobavitelj)",
    "elektro_maribor": "Elektro Maribor (osnovni dobavitelj)",
    "elektro_celje": "Elektro Celje (osnovni dobavitelj)", 
    "elektro_gorenjska": "Elektro Gorenjska (osnovni dobavitelj)",
    "elektro_primorska": "Elektro Primorska (osnovni dobavitelj)",
    "other": "Drug dobavitelj",
}

# Fixed Slovenian holidays (MM-DD format)
FIXED_SLOVENIAN_HOLIDAYS = [
    "01-01",  # New Year's Day
    "01-02",  # New Year's Day (second day)
    "02-08",  # Prešeren Day
    "04-27",  # Day of Uprising Against Occupation
    "05-01",  # Labour Day
    "05-02",  # Labour Day (second day)
    "06-25",  # Statehood Day
    "08-15",  # Assumption Day
    "10-31",  # Reformation Day
    "11-01",  # Remembrance Day
    "12-25",  # Christmas Day
    "12-26",  # Independence and Unity Day
]

def calculate_easter_sunday(year: int) -> date:
    """Calculate Easter Sunday for a given year using the algorithm."""
    # Algorithm for calculating Easter (Gregorian calendar)
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def get_slovenian_holidays_for_year(year: int) -> List[str]:
    """Get all Slovenian holidays for a given year in MM-DD format."""
    holidays = FIXED_SLOVENIAN_HOLIDAYS.copy()
    
    # Calculate dynamic holidays based on Easter
    easter = calculate_easter_sunday(year)
    
    # Easter Monday (day after Easter Sunday)
    easter_monday = easter + timedelta(days=1)
    holidays.append(easter_monday.strftime("%m-%d"))
    
    # Whit Sunday (49 days after Easter)
    whit_sunday = easter + timedelta(days=49)
    holidays.append(whit_sunday.strftime("%m-%d"))
    
    return holidays

def is_holiday(dt: datetime) -> bool:
    """Check if a given datetime is a Slovenian holiday."""
    holidays = get_slovenian_holidays_for_year(dt.year)
    date_str = dt.strftime("%m-%d")
    return date_str in holidays

def get_energy_tariff(dt: datetime) -> str:
    """Determine if time is VT (high) or MT (low) for electrical energy."""
    # VT (Visoka tarifa): Monday-Friday 6:00-22:00
    # MT (Mala tarifa): Monday-Friday 22:00-6:00, all day Saturday, Sunday and holidays
    
    if is_holiday(dt) or dt.weekday() >= 5:  # Weekend or holiday
        return "MT"
    
    # Weekday
    hour = dt.hour
    if 6 <= hour < 22:
        return "VT"
    else:
        return "MT"

def calculate_total_price_per_kwh(dt: datetime, energy_vt_price: float, energy_mt_price: float, 
                                 network_prices: dict, contributions: float, excise: float) -> dict:
    """Calculate total price per kWh including all components."""
    # Get current tariff block for network charges
    season = get_season(dt)
    is_holiday_today = is_holiday(dt)
    
    # Determine network schedule
    if is_holiday_today or dt.weekday() >= 5:  # Weekend (Saturday/Sunday) or holiday
        if season == "higher":
            schedule = WEEKEND_HOLIDAY_SCHEDULE_HIGHER
        else:
            schedule = WEEKEND_HOLIDAY_SCHEDULE_LOWER
    else:  # Monday to Friday (weekdays)
        if season == "higher":
            schedule = WEEKDAY_SCHEDULE_HIGHER
        else:
            schedule = WEEKDAY_SCHEDULE_LOWER

    # Find current tariff block
    current_time = dt.strftime("%H:%M")
    current_block = 3  # default
    
    for slot in schedule:
        start_time = slot["start"]
        end_time = slot["end"]
        if end_time == "24:00":
            end_time = "23:59"
        if start_time <= current_time <= end_time:
            current_block = slot["block"]
            break
    
    # Get energy tariff (VT/MT)
    energy_tariff = get_energy_tariff(dt)
    
    # Calculate total price
    energy_price = energy_vt_price if energy_tariff == "VT" else energy_mt_price
    network_price = network_prices.get(current_block, 0)
    
    total_price = energy_price + network_price + contributions + excise
    
    return {
        "energy_tariff": energy_tariff,
        "energy_price": energy_price,
        "current_block": current_block,
        "network_price": network_price,
        "contributions": contributions,
        "excise_tax": excise,
        "total_price": total_price,
    }

def get_season(dt: datetime) -> str:
    """Determine if date is in higher or lower season."""
    month = dt.month
    # Higher season (Winter): November to February (11,12,1,2) - po slovenskem sistemu
    # Lower season (Summer): March to October (3,4,5,6,7,8,9,10)
    if month in [11, 12, 1, 2]:
        return "higher"
    else:
        return "lower"

# Tariff block schedules - Higher season (October-March)
# Schedule for workdays (Monday to Friday) - Higher season
WEEKDAY_SCHEDULE_HIGHER = [
    {"start": "00:00", "end": "06:00", "block": 3},  # Night
    {"start": "06:00", "end": "07:00", "block": 2},  # Early morning
    {"start": "07:00", "end": "14:00", "block": 1},  # Morning/day peak (most expensive)
    {"start": "14:00", "end": "16:00", "block": 2},  # Afternoon
    {"start": "16:00", "end": "20:00", "block": 1},  # Evening peak (most expensive)
    {"start": "20:00", "end": "22:00", "block": 2},  # Evening
    {"start": "22:00", "end": "24:00", "block": 3},  # Night
]

# Schedule for workdays (Monday to Friday) - Lower season
WEEKDAY_SCHEDULE_LOWER = [
    {"start": "00:00", "end": "06:00", "block": 4},  # Night
    {"start": "06:00", "end": "07:00", "block": 3},  # Early morning
    {"start": "07:00", "end": "14:00", "block": 2},  # Morning/day peak (most expensive)
    {"start": "14:00", "end": "16:00", "block": 3},  # Afternoon
    {"start": "16:00", "end": "20:00", "block": 2},  # Evening peak (most expensive)
    {"start": "20:00", "end": "22:00", "block": 3},  # Evening
    {"start": "22:00", "end": "24:00", "block": 4},  # Night
]

# Schedule for weekends and holidays - Higher season (Saturday, Sunday, holidays)
WEEKEND_HOLIDAY_SCHEDULE_HIGHER = [
    {"start": "00:00", "end": "06:00", "block": 4},  # Night
    {"start": "06:00", "end": "07:00", "block": 3},  # Early morning
    {"start": "07:00", "end": "14:00", "block": 2},  # Day peak (most expensive)
    {"start": "14:00", "end": "16:00", "block": 3},  # Afternoon
    {"start": "16:00", "end": "20:00", "block": 2},  # Evening peak (most expensive)
    {"start": "20:00", "end": "22:00", "block": 3},  # Evening
    {"start": "22:00", "end": "24:00", "block": 4},  # Night
]

# Schedule for weekends and holidays - Lower season (Saturday, Sunday, holidays)
WEEKEND_HOLIDAY_SCHEDULE_LOWER = [
    {"start": "00:00", "end": "06:00", "block": 5},  # Night (cheapest)
    {"start": "06:00", "end": "07:00", "block": 4},  # Early morning
    {"start": "07:00", "end": "14:00", "block": 3},  # Day peak (most expensive)
    {"start": "14:00", "end": "16:00", "block": 4},  # Afternoon
    {"start": "16:00", "end": "20:00", "block": 3},  # Evening peak (most expensive)
    {"start": "20:00", "end": "22:00", "block": 4},  # Evening
    {"start": "22:00", "end": "24:00", "block": 5},  # Night (cheapest)
]

# Legacy schedules for backward compatibility
WEEKDAY_SCHEDULE = WEEKDAY_SCHEDULE_LOWER
WEEKEND_HOLIDAY_SCHEDULE = WEEKEND_HOLIDAY_SCHEDULE_LOWER

# Block descriptions (for network charges - omrežnina)
# Note: Block 1 is most expensive, Block 5 is cheapest
BLOCK_DESCRIPTIONS = {
    1: "Highest rate (peak hours) - Omrežnina",
    2: "High rate - Omrežnina", 
    3: "Medium rate - Omrežnina",
    4: "Low rate - Omrežnina",
    5: "Lowest rate (night/off-peak) - Omrežnina",
}

# Energy tariff descriptions (for electrical energy - električna energija)
ENERGY_DESCRIPTIONS = {
    "VT": "Visoka tarifa (High tariff) - Električna energija",
    "MT": "Mala tarifa (Low tariff) - Električna energija",
}

# Default prices (EUR/kWh) - examples based on 2025 Slovenian electricity market
DEFAULT_PRICES = {
    # Electrical Energy (Električna energija)
    CONF_ENERGY_VT_PRICE: 0.1199,   # VT (visoka tarifa) - working hours
    CONF_ENERGY_MT_PRICE: 0.0979,   # MT (mala tarifa) - off-peak hours
    
    # Network charges (Omrežnina) - by tariff blocks (1=highest, 5=lowest)
    CONF_BLOCK_1_PRICE: 0.01998,     # Block 1 - highest
    CONF_BLOCK_2_PRICE: 0.01833,     # Block 2 - high
    CONF_BLOCK_3_PRICE: 0.01809,     # Block 3 - medium
    CONF_BLOCK_4_PRICE: 0.01855,     # Block 4 - low rate
    CONF_BLOCK_5_PRICE: 0.01873,     # Block 5 - lowest rate (night/off-peak)

    # Additional charges
    CONF_CONTRIBUTIONS_PRICE: 0.000930,  # Prispevki (RES, OVES, etc.)
    CONF_EXCISE_TAX: 0.001530,          # Trošarina
}

# Note: API endpoints for distributors are not currently available
# All prices must be configured manually through the integration UI

# Update intervals
UPDATE_INTERVAL_TARIFF = 60  # Check tariff block every minute
UPDATE_INTERVAL_PRICES = 3600 * 24  # Update prices once per day

# Season information for UI
SEASON_INFO = {
    "higher": {
        "name": "Višja sezona",
        "months": "November - Februar",
        "description": "Zimska tarifa z višjimi tarifami v koničnih urah"
    },
    "lower": {
        "name": "Nižja sezona", 
        "months": "Marec - Oktober",
        "description": "Poletna tarifa z nižjimi tarifami"
    }
}
