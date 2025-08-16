# CEZ HDO Sensor - Home Assistant Integration

[![GitHub release](https://img.shields.io/github/release/kubroid/cez-hdo-sensor.svg)](https://github.com/kubroid/cez-hdo-sensor/releases)

🏠 **Built-in version** of CEZ HDO Sensor for Home Assistant - works without HACS and additional dependencies!

[🇷🇺 Русская версия](README_RU.md) | [🇨🇿 Česká verze](README_CS.md)

## ✨ Features

- 📡 **Signal Support**: a3b4dp01, a3b4dp02, a3b4dp06
- ⚡ **Minute Updates**: Instant HDO switching without delays
- 🧠 **Smart Caching**: Schedule updates hourly, state updates every minute
- 🚀 **Easy Installation**: Copy folder and restart
- 🔧 **No Dependencies**: No HACS or Docker required
- 🌐 **Multilingual**: Russian, English, Czech
- 🛡️ **Stability**: Works even during CEZ API issues
- 📊 **Monitoring**: Schedule age tracking and diagnostics
- 🚨 **Error Monitoring**: Dedicated error sensor for system health
- 🎨 **Dynamic Icons**: Visual feedback based on tariff state

## 📦 Installation

### 🏪 HACS Installation (Recommended)

1. **Install HACS** if you haven't already: [HACS Installation Guide](https://hacs.xyz/docs/setup/download)
2. **Add Custom Repository**:
   - Go to HACS → Integrations
   - Click the three dots menu (⋮) → Custom repositories
   - Add repository URL: `https://github.com/kubroid/cez-hdo-sensor`
   - Category: Integration
   - Click "Add"
3. **Install Integration**:
   - Search for "CEZ HDO Sensor" in HACS
   - Click "Download" → "Download"
4. **Restart Home Assistant**
5. **Add Integration**: Settings → Devices & Services → Add Integration → "CEZ HDO Sensor"

### 🚀 Quick Installation (Manual)

1. **Download archive**: [Download ZIP](https://github.com/kubroid/cez-hdo-sensor/archive/builtin-integration.zip)
2. **Extract** to `/config/custom_components/` folder
3. **Restart** Home Assistant
4. **Add integration**: Settings → Devices & Services → Add Integration → "CEZ HDO Sensor"

### 📁 Manual Installation

```bash
# In Home Assistant config folder:
cd /config/custom_components/
wget https://github.com/kubroid/cez-hdo-sensor/archive/builtin-integration.zip
unzip builtin-integration.zip
mv cez-hdo-sensor-builtin-integration/custom_components/cez_hdo .
rm -rf cez-hdo-sensor-builtin-integration builtin-integration.zip

# Restart Home Assistant
```

## ⚙️ Configuration

### 📋 Required Information

You need two pieces of information:

1. **EAN Code**: 18-digit number from your electricity bill
2. **HDO Signal**: Choose from:
   - `a3b4dp01` (standard, default)
   - `a3b4dp02` (alternative)
   - `a3b4dp06` (special schedule)

### 🔧 Setup Steps

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **"CEZ HDO Sensor"**
4. Enter your **EAN code** and select **HDO signal**
5. Click **Submit**

## 📡 Sensors

After setup, two binary sensors will be created:

### 📡 Main HDO Sensor
- **Name**: `binary_sensor.cez_hdo_[your_ean]`
- **States**:
  - `ON` - Low tariff active (HDO enabled) ⚡
  - `OFF` - Normal tariff (HDO disabled) ⚡
- **Icon**:
  - `mdi:flash` when low tariff is active
  - `mdi:flash-outline` when normal tariff is active

### 🚨 Error Monitoring Sensor
- **Name**: `binary_sensor.cez_hdo_error_[your_ean]`
- **States**:
  - `ON` - System error detected (safety mode active)
  - `OFF` - System operating normally
- **Functions**:
  - 🛡️ Shows monitoring system status
  - ⚠️ Alerts about API or network issues
  - 📊 Displays error messages in attributes

## 🔄 Using in Automations

### Basic HDO Control

```yaml
automation:
  - alias: "Turn on water heater during low tariff"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_123456789012345678
        to: 'on'
    action:
      - service: switch.turn_on
        entity_id: switch.water_heater

  - alias: "Turn off water heater during normal tariff"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_123456789012345678
        to: 'off'
    action:
      - service: switch.turn_off
        entity_id: switch.water_heater
```

### Error Monitoring

```yaml
automation:
  # Error detection automation
  - alias: "CEZ HDO - System Error Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_error_123456789012345678
        to: 'on'
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ CEZ HDO - System Error"
          message: >
            HDO system error detected.
            Safety mode activated (low tariff).
            Error: {{ trigger.to_state.attributes.error_message }}

  # System recovery automation
  - alias: "CEZ HDO - System Recovered"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_error_123456789012345678
        to: 'off'
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "✅ CEZ HDO - System Recovered"
          message: "CEZ HDO system returned to normal operation"
```

## 🛠️ Technical Details

### 🔧 Supported Signals

The integration supports all standard CEZ HDO signals:

- **a3b4dp01**: Standard HDO signal (default)
- **a3b4dp02**: Alternative HDO signal
- **a3b4dp06**: Special HDO signal with different schedule

Choose the signal that matches your electricity provider contract.

### 🛡️ Error Handling and Safety

The integration has multi-level safety mechanisms:

#### 🔧 Automatic Error Handling
- **Safety Mode**: Any problems (no internet, API errors, parsing issues) automatically trigger safety mode
- **Low Tariff Default**: During errors, low tariff is always activated to protect from high bills
- **Always Available**: Sensors remain available even during errors

#### 📊 Dual Status Indication
- **Main Sensor** (`binary_sensor.cez_hdo_[ean]`): Shows HDO status (ON/OFF)
- **Error Sensor** (`binary_sensor.cez_hdo_error_[ean]`): Shows monitoring system status
- **Error Attributes**: Detailed error information in sensor attributes

#### 🚨 Types of Monitored Errors
- 🌐 **Network Errors**: Connection issues to API
- 🔧 **API Errors**: CEZ service unavailability
- 📊 **Parsing Errors**: Data processing issues
- ⏰ **Schedule Errors**: Outdated or incorrect data

#### ⚡ Behavior During Errors
```
Error → Safety Mode → Low Tariff ON → Notification
```

## 🌍 Supported Languages

- 🇺🇸 **English** (en)
- 🇷🇺 **Русский** (ru) - [README_RU.md](README_RU.md)
- 🇨🇿 **Čeština** (cs)

## Troubleshooting

### Sensor shows "Unavailable"

1. Check if EAN code is correct
2. Ensure internet connection is available
3. Check Home Assistant logs for errors

### Data not updating

1. Component updates data every hour
2. Check CEZ Distribuce API availability
3. Restart Home Assistant

### Wrong schedule

1. Verify your HDO signal selection (a3b4dp01, a3b4dp02, a3b4dp06)
2. Check with your electricity provider
3. Look at sensor attributes for detailed schedule

## Support

If you have questions or issues, please create an issue in the GitHub repository.

## License

This project is distributed under the MIT License.
