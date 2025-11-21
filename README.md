# Slovenian Electricity Costs

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/49jan/hass-slovenian-electricity-costs)](https://github.com/49jan/hass-slovenian-electricity-costs/releases)
[![GitHub](https://img.shields.io/github/license/49jan/hass-slovenian-electricity-costs)](LICENSE)

A comprehensive Home Assistant integration for calculating electricity costs using the **Slovenian tariff system** with separated pricing components (energy + network + contributions + excise tax) and full seasonal/holiday support.

## Key Features ✨

- **🗓️ Seasonal Tariffs**: Complete support for higher (November-February) and lower (March-October) seasons
- **🎉 Slovenian Holidays**: Dynamic calculation of all Slovenian holidays including Easter-based dates
- **⚡ VT/MT Energy Tariffs**: High tariff (VT) and low tariff (MT) for electrical energy
- **🔌 Network Tariff Blocks 1-5**: Network charges (omrežnina) based on time, day, and season
- **💰 Complete Price Structure**: Energy + Network + Contributions + Excise Tax
- **📊 Energy Dashboard**: Integration with Home Assistant Energy tab
- **🤖 Automation Support**: Binary sensors for easy device automation
- **📈 Cost Tracking**: Real-time cost calculation based on consumption
- **🎯 6-Decimal Precision**: Accurate pricing to 0.000001 EUR/kWh

## Slovenian Electricity Price Structure 💰

**Total electricity price consists of 4 components:**

1. **Electrical Energy** (VT/MT tariffs)
   - VT (High Tariff): Working days 06:00-22:00
   - MT (Low Tariff): Off-peak hours, weekends, holidays

2. **Network Charges** (Tariff Blocks 1-5) 
   - Distribution network costs (omrežnina)
   - Based on time, day, and season

3. **Contributions** 
   - Regulatory contributions (RES, OVES, etc.)

4. **Excise Tax**
   - Government excise tax on electricity

## Network Tariff Block System 🕐

### Higher Season (November - February)
**Working days (Monday-Friday):**
- `00:00-06:00`: **Block 3**
- `06:00-07:00`: **Block 2**
- `07:00-14:00`: **Block 1**
- `14:00-16:00`: **Block 2**
- `16:00-20:00`: **Block 1**
- `20:00-22:00`: **Block 2**
- `22:00-24:00`: **Block 3**

**Weekends & Holidays:**
- `00:00-06:00`: **Block 4**
- `06:00-07:00`: **Block 3**
- `07:00-14:00`: **Block 2**
- `14:00-16:00`: **Block 3**
- `16:00-20:00`: **Block 2**
- `20:00-22:00`: **Block 3**
- `22:00-24:00`: **Block 4**

### Lower Season (March - October)
**Working days (Monday-Friday):**
- `00:00-06:00`: **Block 4**
- `06:00-07:00`: **Block 3**
- `07:00-14:00`: **Block 2**
- `14:00-16:00`: **Block 3**
- `16:00-20:00`: **Block 2**
- `20:00-22:00`: **Block 3**
- `22:00-24:00`: **Block 4**

**Weekends & Holidays:**
- `00:00-06:00`: **Block 5**
- `06:00-07:00`: **Block 4**
- `07:00-14:00`: **Block 3**
- `14:00-16:00`: **Block 4**
- `16:00-20:00`: **Block 3**
- `20:00-22:00`: **Block 4**
- `22:00-24:00`: **Block 5**

## Price Hierarchy

- **Block 1**: 0.01998 EUR/kWh
- **Block 2**: 0.01833 EUR/kWh
- **Block 3**: 0.01809 EUR/kWh
- **Block 4**: 0.01855 EUR/kWh
- **Block 5**: 0.01873 EUR/kWh
---

## Installation 📦

### Via HACS (Recommended)
1. Add this repository as a custom repository in HACS
2. Search for "Slovenian Electricity Costs" in HACS
3. Install the integration
4. Restart Home Assistant

### Manual Installation
1. Download the `custom_components/slovenian_electricity_costs/` folder
2. Copy it to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Add the integration via UI

---

## Configuration ⚙️

### Initial Setup:
1. **Settings** → **Devices & Services** → **Add Integration**
2. Search for **"Slovenian Electricity Costs"**
3. **Select your electricity supplier** (GEN-I, Petrol, Elektro Energija, etc.)
4. **Optional** - Select energy consumption sensor for monitoring
5. **Enter SEPARATE prices** (EUR/kWh):

   **ENERGY TARIFFS:**
   - **VT Price**: 0.1199 EUR (high tariff, working hours)
   - **MT Price**: 0.0979 EUR (low tariff, off-peak)

   **NETWORK CHARGES (tariff blocks):**
   - **Block 1**: 0.01998 EUR/kWh
   - **Block 2**: 0.01833 EUR/kWh
   - **Block 3**: 0.01809 EUR/kWh
   - **Block 4**: 0.01855 EUR/kWh
   - **Block 5**: 0.01873 EUR/kWh

   **ADDITIONAL COSTS:**
   - **Contributions**: 0.000930 EUR (RES, OVES, etc.)
   - **Excise Tax**: 0.001530 EUR (government tax)

> **Important**: You must enter SEPARATE prices for all components! Tariff blocks are only network charges, not total electricity price.

---

## Sensors & Entities 📊

### Main Sensors:
```yaml
sensor.current_tariff_block              # Current network tariff block (1-5)
sensor.current_energy_tariff             # Current energy tariff (VT/MT)
sensor.current_total_electricity_price   # Total current price (all components)
sensor.current_season                    # Current season (higher/lower)
sensor.holiday_status                   # Holiday status (Holiday/Working Day)
sensor.electricity_cost                # Calculated electricity cost (EUR)
```

### Price Components:
```yaml
sensor.energy_vt_price                  # VT energy price
sensor.energy_mt_price                  # MT energy price
sensor.block_1_price                   # Network charge block 1
sensor.block_2_price                   # Network charge block 2
sensor.block_3_price                   # Network charge block 3
sensor.block_4_price                   # Network charge block 4
sensor.block_5_price                   # Network charge block 5
sensor.contributions_price             # Contributions
sensor.excise_tax                     # Excise tax
```

### Binary Sensors for Automations:
```yaml
binary_sensor.tariff_block_1_active    # Is block 1 active
binary_sensor.tariff_block_2_active    # Is block 2 active
binary_sensor.tariff_block_3_active    # Is block 3 active
binary_sensor.tariff_block_4_active    # Is block 4 active
binary_sensor.tariff_block_5_active    # Is block 5 active

binary_sensor.higher_season            # Is higher season active
binary_sensor.holiday_today            # Is today a holiday
binary_sensor.cheap_electricity        # Cheap rates (blocks 4-5)
binary_sensor.expensive_electricity    # Expensive rates (blocks 1-2)
```

---

## Services 🛠️

### 1. Manual Price Updates:
```yaml
service: slovenian_electricity_costs.update_prices
data:
  energy_vt_price: 0.1199
  energy_mt_price: 0.0979
  block_1_price: 0.01998
  block_2_price: 0.01833
  block_3_price: 0.01809
  block_4_price: 0.01855
  block_5_price: 0.01873
  contributions_price: 0.000930
  excise_tax: 0.001530
```

### 2. Get Current Status:
```yaml
service: slovenian_electricity_costs.get_current_block
# Fires event with detailed current status
```

### 3. Calculate Cost:
```yaml
service: slovenian_electricity_costs.calculate_cost
data:
  consumption_kwh: 15.5
# Fires event with calculated cost
```

---

## Automation Examples 🏠

### 1. Turn On Water Heater During Cheap Rates:
```yaml
automation:
  - alias: "Water Heater ON - Cheap Electricity"
    trigger:
      - platform: state
        entity_id: binary_sensor.cheap_electricity
        to: "on"
    action:
      - service: switch.turn_on
        entity_id: switch.water_heater
```

### 2. Turn Off Appliances During Most Expensive Rate:
```yaml
automation:
  - alias: "Appliances OFF - Block 1 Most Expensive"
    trigger:
      - platform: state
        entity_id: binary_sensor.tariff_block_1_active
        to: "on"
    action:
      - service: switch.turn_off
        target:
          entity_id: 
            - switch.washing_machine
            - switch.dishwasher
      - service: notify.mobile_app
        data:
          title: "⚠️ Most Expensive Rate!"
          message: "Block 1 active ({{states('sensor.current_total_electricity_price')}}€/kWh)"
```

### 3. Holiday Rate Notification:
```yaml
automation:
  - alias: "Holiday Rate Notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.holiday_today
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "🎉 Holiday Today!"
          message: "Holiday rates apply - great time for energy-intensive activities!"
```

---

## Supported Slovenian Holidays 🇸🇮

### Fixed Holidays:
- New Year's Day (1st, 2nd January)
- Prešeren Day (8th February)
- Day of Uprising Against Occupation (27th April)
- Labour Day (1st, 2nd May)
- Statehood Day (25th June)
- Assumption Day (15th August)
- Reformation Day (31st October)
- Remembrance Day (1st November)
- Christmas Day (25th December)
- Independence and Unity Day (26th December)

### Dynamic Holidays (calculated):
- Easter Monday
- Whit Monday (49 days after Easter)

---

## Energy Dashboard Integration 📈

The integration automatically adds the `sensor.electricity_cost` to Home Assistant Energy Dashboard for:
- Daily cost tracking
- Monthly consumption analysis
- Annual comparisons
- Consumption optimization based on tariffs

---

## Contributing & Support 🤝

If you have suggestions, find bugs, or need help:
1. Create an **Issue** on GitHub
2. Suggest improvements via **Pull Request**
3. Help improve documentation

---

## License 📄

MIT License - see [LICENSE](LICENSE) file for details.

---

**Author**: 49Jan  
**Version**: 1.0.0  
**Last Updated**: November 2025

*This integration is not officially associated with any Slovenian electricity distributors. All prices must be entered manually or updated according to current tariffs from your supplier. Remember that total electricity price consists of multiple components: energy (VT/MT) + network (blocks 1-5) + contributions + excise tax.*