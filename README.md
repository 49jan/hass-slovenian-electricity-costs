# Slovenian Electricity Costs

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/byJan/slovenian_electricity_costs)](https://github.com/byJan/slovenian_electricity_costs/releases)
[![GitHub](https://img.shields.io/github/license/byJan/slovenian_electricity_costs)](LICENSE)

Home Assistant integracija za računanje cene elektrike po slovenskem sistemu z **ločenim prispevnim sistemom za energijo in omrežnino ter popolno podporo za sezone in praznike**.

## Ključne Funkcionalnosti ✨

- **🗓️ Sezonska Tarifikacija**: Popolno upoštevanje višje (november-februar) in nižje (marec-oktober) sezone
- **🎉 Slovenski Prazniki**: Dinamično računanje vseh slovenskih praznikov vključno z velikonočnimi
- **⚡ VT/MT Energijske Tarife**: Visoka tarifa (VT) in mala tarifa (MT) za energijo
- **🔌 Tarifni Bloki 1-5**: Omrežnina (network charges) glede na čas, dan in sezono
- **💰 Popolna Cenovna Struktura**: Energija + Omrežnina + Prispevki + Trošarina
- **📊 Energy Dashboard**: Integracija s Home Assistant Energy zavihkom
- **🤖 Avtomatizacije**: Binarne senzorje za enostavno avtomatizacijo naprav
- **📈 Sledenje Stroškov**: Realno računanje stroškov na podlagi porabe

## Slovenska Cenovna Struktura Elektrike 💰

**Skupna cena elektrike se sestavlja iz 4 komponent:**

1. **Električna Energija** (VT/MT tariifi)
   - VT (Visoka Tarifa): delava dni 06:00-22:00
   - MT (Mala Tarifa): ostali čas, vikendi, prazniki

2. **Omrežnina** (Tarifni Bloki 1-5) 
   - Stroški distribucije električnega omrežja
   - Odvisni od časa, dneva in sezone

3. **Prispevki** 
   - Regulativni prispevki (AGEN-RS, OVE, itd.)

4. **Trošarina**
   - Državna trošarina na električno energijo

## Tarifni Sistem za Omrežnino 🕐

### Višja Sezona (November - Februar)
**Delovni dnevi (pon-pet):**
- `00:00-06:00`: **Blok 1** (Zelo poceni nočni)
- `06:00-10:00`: **Blok 5** ⚠️ (Najvišji vrh - zimska konica)
- `10:00-14:00`: **Blok 3** (Srednji)
- `14:00-16:00`: **Blok 4** (Visok vrh)
- `16:00-20:00`: **Blok 5** ⚠️ (Najvišji vrh - večerna konica)
- `20:00-22:00`: **Blok 4** (Visok)
- `22:00-24:00`: **Blok 2** (Nizek nočni)

### Nižja Sezona (Marec - Oktober)  
**Delovni dnevi (pon-pet):**
- `00:00-06:00`: **Blok 1** (Zelo poceni nočni)
- `06:00-10:00`: **Blok 4** (Jutranji vrh)
- `10:00-14:00`: **Blok 3** (Srednji)
- `14:00-16:00`: **Blok 4** (Popoldanski vrh)
- `16:00-20:00`: **Blok 3** (Večerni)
- `20:00-22:00`: **Blok 3** (Večerni)
- `22:00-24:00`: **Blok 2** (Nočni)

> **Pomembno**: Blok 5 se uporablja **samo v višji sezoni** med koničnimi urami!

### Vikendi in Prazniki
- **Sobote**: Blok 1-3 (odvisno od sezone)
- **Nedelje in prazniki**: Pretežno blok 1-2

## Namestitev 📦

### Preko HACS (priporočeno)
1. Dodajte ta repozitorij v HACS kot custom repository
2. Poiščite "Slovenian Electricity Costs" v HACS
3. Namestite integracijo
4. Ponovno zaženite Home Assistant

### Ročno
1. Prenesite datoteke v `custom_components/slovenian_electricity_costs/`
2. Ponovno zaženite Home Assistant
3. Dodajte integracijo preko UI

## Konfiguracija ⚙️

1. **Settings** → **Devices & Services** → **Add Integration**
2. Poiščite **"Slovenian Electricity Costs"**
3. Izberite dobavitelja elektrike (GEN-I, Elektro Energija, itd.)
4. Opcijsko izberite senzor porabe elektrike
5. Vnesite cene za **vse komponente** (€/kWh):
   - **Energijske tarife**: VT in MT cene
   - **Omrežnina**: Tarifi bloki 1-5
   - **Prispevki**: Regulativni prispevki
   - **Trošarina**: Državna trošarina

> **Pomembno**: Vnesti morate ločene cene za vse komponente! Tarifni bloki so le del omrežnine, ne celotne cene elektrike.

## Senzorji 📊

### Glavni Senzorji
- `sensor.current_tariff_block` - Trenutni tarifni blok za omrežnino (1-5)
- `sensor.current_energy_tariff` - Trenutna energijska tarifa (VT/MT)
- `sensor.current_electricity_price` - Skupna trenutna cena elektrike (€/kWh)
- `sensor.current_season` - Trenutna sezona (Višja/Nižja)
- `sensor.holiday_status` - Status praznika (Holiday/Working Day)
- `sensor.electricity_cost` - Izračunan strošek elektrike (€)

### Cene Po Komponentah
- `sensor.energy_vt_price` in `sensor.energy_mt_price` - Energijske tarife
- `sensor.block_1_price` do `sensor.block_5_price` - Omrežnina po tarifnih blokih
- `sensor.contributions_price` - Prispevki
- `sensor.excise_tax` - Trošarina

### Binarski Senzorji za Avtomatizacije 🤖
- `binary_sensor.tariff_block_1_active` do `binary_sensor.tariff_block_5_active`
- `binary_sensor.higher_season` - Ali je višja sezona
- `binary_sensor.holiday_today` - Ali je danes praznik
- `binary_sensor.cheap_electricity` - Poceni elektriko (bloki 1-2)
- `binary_sensor.expensive_electricity` - Draga elektriko (bloki 4-5)

## Primeri Avtomatizacij 🏠

### Bojler med Poceni Elektriko
```yaml
automation:
  - alias: "Vklopi bojler med poceni elektr"
    trigger:
      - platform: state
        entity_id: binary_sensor.cheap_electricity
        to: "on"
    action:
      - service: switch.turn_on
        entity_id: switch.water_heater
```

### Izklopi Naprave v Višji Sezoni - Blok 5
```yaml
automation:
  - alias: "Izklopi porabnike v bloku 5"
    trigger:
      - platform: state
        entity_id: binary_sensor.tariff_block_5_active
        to: "on"
    condition:
      - condition: state
        entity_id: binary_sensor.higher_season
        state: "on"
    action:
      - service: switch.turn_off
        target:
          entity_id: 
            - switch.washing_machine
            - switch.dishwasher
      - service: notify.mobile_app
        data:
          title: "⚠️ Najvišja tarifa!"
          message: "Aktiven blok 5 ({{ states('sensor.current_electricity_price') }}€/kWh) - porabniki izklopljeni"
```

### Obvestilo o Praznikih
```yaml
automation:
  - alias: "Obvestilo praznična tarifa"
    trigger:
      - platform: state
        entity_id: binary_sensor.holiday_today
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "🎉 Danes je praznik"
          message: "Velja praznična tarifa - idealen čas za pranje in pomivanje!"
```

## Servisi 🛠️

### `slovenian_electricity_costs.update_prices`
Ročno posodabljanje cen za vse tarifne bloke

### `slovenian_electricity_costs.get_current_block`  
Pridobi podrobne informacije o trenutnem stanju (blok, sezona, praznik)

### `slovenian_electricity_costs.calculate_cost`
Izračuna strošek elektrike za podano porabo

## Podprti Slovenski Prazniki 🇸🇮

**Fiksni prazniki:**
- Nova leto (1., 2. januar)
- Prešernov dan (8. februar)
- Dan upora (27. april) 
- Praznik dela (1., 2. maj)
- Dan državnosti (25. junij)
- Marijino vnebovzetje (15. avgust)
- Dan reformacije (31. oktober)
- Dan spomina (1. november)
- Božič (25. december)
- Dan neodvisnosti (26. december)

**Dinamični prazniki (računani):**
- Velikonočni ponedeljek
- Binkošti

## Energijski Pregled 📈

Integracija avtomatsko dodeli senzor `sensor.electricity_cost` v Home Assistant Energy Dashboard za:
- Dnevno sledenje stroškov
- Mesečne analize porabe  
- Letne primerjave
- Optimizacija porabe glede na tarife

## Prispevki in Podpora 🤝

Če imate predloge, najdete napako ali potrebujete pomoč:
1. Ustvarite **Issue** na GitHubu
2. Predlagajte izboljšave preko **Pull Request**
3. Pomagajte izboljšati dokumentacijo

## Licenca 📄

MIT License - see [LICENSE](LICENSE) file for details.

---

**Avtor**: byJan  
**Verzija**: 1.0.0  
**Poslednja posodobitev**: November 2025

*Ta integracija ni uradno povezana z nobenimi slovenskimi dobavitelji elektrike. Vse cene je potrebno vnesti ročno ali posodobiti glede na aktualne tarife vašega dobavitelja. Ne pozabite, da se skupna cena elektrike sestavi iz več komponent: energija (VT/MT) + omrežnina (bloki 1-5) + prispevki + trošarina.*