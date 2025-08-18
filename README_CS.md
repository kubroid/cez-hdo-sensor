# CEZ HDO Sensor - Integrace pro Home Assistant

[![GitHub release](https://img.shields.io/github/release/kubroid/cez-hdo-sensor.svg)](https://github.com/kubroid/cez-hdo-sensor/releases)

🏠 **Vestavěná verze** CEZ HDO Sensor pro Home Assistant - funguje bez HACS a dalších závislostí!

[🇺🇸 English version](README.md) | [🇷🇺 Русская версия](README_RU.md)

## ✨ Funkce

- 📡 **Podpora signálů**: a3b4dp01, a3b4dp02, a3b4dp06
- ⚡ **Minutové aktualizace**: Okamžité přepínání HDO bez zpoždění
- 🧠 **Chytré ukládání**: Rozvrh se aktualizuje každou hodinu, stav každou minutu
- 🚀 **Snadná instalace**: Zkopírovat složku a restartovat
- 🔧 **Bez závislostí**: Nepotřebuje HACS nebo Docker
- 🌐 **Vícejazyčnost**: Ruština, angličtina, čeština
- 🛡️ **Stabilita**: Funguje i při problémech s CEZ API
- 📊 **Monitoring**: Sledování stáří rozvrhu a diagnostika
- 🚨 **Monitoring chyb**: Vyhrazený senzor pro kontrolu stavu systému
- 🎨 **Dynamické ikony**: Vizuální zpětná vazba podle stavu tarifu

## 📦 Instalace

### 🏪 Instalace přes HACS (Doporučeno)

1. **Nainstalujte HACS** pokud ještě nemáte: [Průvodce instalací HACS](https://hacs.xyz/docs/setup/download)
2. **Přidejte vlastní repozitář**:
   - Jděte do HACS → Integrations
   - Klikněte na menu se třemi tečkami (⋮) → Custom repositories
   - Přidejte URL repozitáře: `https://github.com/kubroid/cez-hdo-sensor`
   - Kategorie: Integration
   - Klikněte "Add"
3. **Nainstalujte integraci**:
   - Vyhledejte "CEZ HDO Sensor" v HACS
   - Klikněte "Download" → "Download"
4. **Restartujte Home Assistant**
5. **Přidejte integraci**: Settings → Devices & Services → Add Integration → "CEZ HDO Sensor"

### 🚀 Rychlá instalace (Ručně)

1. **Stáhněte archiv**: [Stáhnout ZIP](https://github.com/kubroid/cez-hdo-sensor/archive/builtin-integration.zip)
2. **Rozbalte** do složky `/config/custom_components/`
3. **Restartujte** Home Assistant
4. **Přidejte integraci**: Settings → Devices & Services → Add Integration → "CEZ HDO Sensor"

### 📁 Ruční instalace

```bash
# Ve složce config Home Assistant:
cd /config/custom_components/
wget https://github.com/kubroid/cez-hdo-sensor/archive/builtin-integration.zip
unzip builtin-integration.zip
mv cez-hdo-sensor-builtin-integration/custom_components/cez_hdo .
rm -rf cez-hdo-sensor-builtin-integration builtin-integration.zip

# Restartujte Home Assistant
```

## ⚙️ Konfigurace

### 📋 Potřebné informace

Budete potřebovat dvě informace:

1. **EAN kód**: 18místné číslo z vašeho účtu za elektřinu
2. **HDO signál**: Vyberte z:
   - `a3b4dp01` (standardní, výchozí)
   - `a3b4dp02` (alternativní)
   - `a3b4dp06` (speciální rozvrh)

### 🔧 Kroky nastavení

1. Jděte do **Settings** → **Devices & Services**
2. Klikněte **Add Integration**
3. Vyhledejte **"CEZ HDO Sensor"**
4. Zadejte váš **EAN kód** a vyberte **HDO signál**
5. Klikněte **Submit**

## 📡 Senzory

Po nastavení budou vytvořeny dva binární senzory:

### 📡 Hlavní HDO senzor
- **Název**: `binary_sensor.cez_hdo_[váš_ean]`
- **Stavy**:
  - `ON` - Aktivní nízký tarif (HDO zapnuté) ⚡
  - `OFF` - Normální tarif (HDO vypnuté) ⚡
- **Ikona**:
  - `mdi:flash` když je aktivní nízký tarif
  - `mdi:flash-outline` když je aktivní normální tarif

### 🚨 Senzor monitorování chyb
- **Název**: `binary_sensor.cez_hdo_error_[váš_ean]`
- **Stavy**:
  - `ON` - Detekována chyba systému (aktivní bezpečný režim)
  - `OFF` - Systém funguje normálně
- **Funkce**:
  - 🛡️ Zobrazuje stav monitorovacího systému
  - ⚠️ Upozorňuje na problémy s API nebo sítí
  - 📊 Zobrazuje chybové zprávy v atributech

## 🔄 Použití v automatizacích

### Základní HDO ovládání

```yaml
automation:
  - alias: "Zapnout ohřívač vody během nízkého tarifu"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_123456789012345678
        to: 'on'
    action:
      - service: switch.turn_on
        entity_id: switch.water_heater

  - alias: "Vypnout ohřívač vody během normálního tarifu"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_123456789012345678
        to: 'off'
    action:
      - service: switch.turn_off
        entity_id: switch.water_heater
```

### Monitoring chyb

```yaml
automation:
  # Automatizace detekce chyb
  - alias: "CEZ HDO - Upozornění na chybu systému"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_error_123456789012345678
        to: 'on'
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ CEZ HDO - Chyba systému"
          message: >
            Detekována chyba systému HDO.
            Aktivován bezpečný režim (nízký tarif).
            Chyba: {{ trigger.to_state.attributes.error_message }}

  # Automatizace obnovení systému
  - alias: "CEZ HDO - Systém obnoven"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_error_123456789012345678
        to: 'off'
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "✅ CEZ HDO - Systém obnoven"
          message: "Monitorovací systém CEZ HDO se vrátil k normálnímu provozu"
```

## 🛠️ Technické detaily

### 🔧 Podporované signály

Integrace podporuje všechny standardní CEZ HDO signály:

- **a3b4dp01**: Standardní HDO signál (výchozí)
- **a3b4dp02**: Alternativní HDO signál
- **a3b4dp06**: Speciální HDO signál s jiným rozvrhem

Vyberte signál, který odpovídá vaší smlouvě s dodavatelem elektřiny.

### 🛡️ Zpracování chyb a bezpečnost

Integrace má víceúrovňové bezpečnostní mechanismy:

#### 🔧 Automatické zpracování chyb
- **Bezpečný režim**: Jakékoli problémy (žádný internet, chyby API, problémy s parsováním) automaticky spustí bezpečný režim
- **Výchozí nízký tarif**: Při chybách je vždy aktivován nízký tarif pro ochranu před vysokými účty
- **Vždy dostupné**: Senzory zůstávají dostupné i při chybách

#### 📊 Dvojitá indikace stavu
- **Hlavní senzor** (`binary_sensor.cez_hdo_[ean]`): Zobrazuje stav HDO (ON/OFF)
- **Senzor chyb** (`binary_sensor.cez_hdo_error_[ean]`): Zobrazuje stav monitorovacího systému
- **Atributy chyb**: Podrobné informace o chybách v atributech senzoru

#### 🚨 Typy monitorovaných chyb
- 🌐 **Síťové chyby**: Problémy s připojením k API
- 🔧 **Chyby API**: Nedostupnost služby CEZ
- 📊 **Chyby parsování**: Problémy se zpracováním dat
- ⏰ **Chyby rozvrhu**: Zastaralá nebo nesprávná data

#### ⚡ Chování při chybách
```
Chyba → Bezpečný režim → Nízký tarif ON → Oznámení
```

## 🌍 Podporované jazyky

- 🇺🇸 **English** (en) - [README.md](README.md)
- 🇷🇺 **Русский** (ru) - [README_RU.md](README_RU.md)
- 🇨🇿 **Čeština** (cs)

## Řešení problémů

### Senzor zobrazuje "Unavailable"

1. Zkontrolujte správnost EAN kódu
2. Ujistěte se, že je k dispozici připojení k internetu
3. Zkontrolujte logy Home Assistant na chyby

### Data se neaktualizují

1. Komponenta aktualizuje data každou hodinu
2. Zkontrolujte dostupnost CEZ Distribuce API
3. Restartujte Home Assistant

### Špatný rozvrh

1. Ověřte výběr vašeho HDO signálu (a3b4dp01, a3b4dp02, a3b4dp06)
2. Zkontrolujte u vašeho dodavatele elektřiny
3. Podívejte se na atributy senzoru pro podrobný rozvrh

## Podpora

Pokud máte otázky nebo problémy, vytvořte prosím issue v GitHub repozitáři.

## Licence

Tento projekt je distribuován pod licencí MIT.
