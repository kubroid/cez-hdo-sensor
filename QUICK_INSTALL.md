# 🚀 Быстрая установка CEZ HDO Sensor

## 📥 Метод 1: Через HACS (Рекомендуется)

### 1. Добавить репозиторий в HACS
1. Откройте **HACS** → **Integrations**
2. Нажмите **⋮** (три точки) → **Custom repositories**
3. Введите URL: `https://github.com/your-username/cez-hdo-sensor`
4. Категория: **Integration**
5. Нажмите **Add**

### 2. Установить интеграцию
1. Найдите "CEZ HDO Sensor" в HACS
2. Нажмите **Download**
3. **Перезапустите Home Assistant**

### 3. Настроить интеграцию
1. **Settings** → **Devices & Services** → **Add Integration**
2. Найдите "CEZ HDO Sensor"
3. Введите:
   - **EAN код** вашего счетчика
   - **HDO сигнал** (a3b4dp01/a3b4dp02/a3b4dp06)
4. Нажмите **Submit**

---

## 📁 Метод 2: Ручная установка

### 1. Скачать файлы
```bash
wget https://github.com/your-username/cez-hdo-sensor/archive/main.zip
unzip main.zip
```

### 2. Скопировать в Home Assistant
```bash
# Путь к вашему Home Assistant config
cp -r cez-hdo-sensor-main/custom_components/cez_hdo /config/custom_components/
```

### 3. Структура должна быть:
```
/config/custom_components/cez_hdo/
├── __init__.py
├── api.py
├── binary_sensor.py
├── config_flow.py
├── const.py
├── coordinator.py
├── manifest.json
├── strings.json
└── translations/
    ├── cs.json
    ├── en.json
    └── ru.json
```

### 4. Перезапустить и настроить
1. **Перезапустите Home Assistant**
2. **Settings** → **Devices & Services** → **Add Integration**
3. Настройте как в методе 1

---

## 🎯 Результат

После установки получите:
- **Бинарный сенсор**: `binary_sensor.cez_hdo_[ваш_ean]`
- **ON** = Низкий тариф активен 🟢
- **OFF** = Обычный тариф 🔴
- **Атрибуты**: время переключений, расписание на день

## 🤖 Пример автоматизации

```yaml
automation:
  - alias: "Бойлер по HDO"
    trigger:
      platform: state
      entity_id: binary_sensor.cez_hdo_859182400123456789
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: binary_sensor.cez_hdo_859182400123456789
                state: "on"
            sequence:
              - service: switch.turn_on
                entity_id: switch.water_heater
          - conditions:
              - condition: state
                entity_id: binary_sensor.cez_hdo_859182400123456789
                state: "off"
            sequence:
              - service: switch.turn_off
                entity_id: switch.water_heater
```

## ❓ Проблемы?

1. **Сенсор "Unavailable"** → Проверьте EAN код
2. **Не обновляется** → Проверьте интернет
3. **Неправильный сигнал** → Попробуйте другой сигнал

**Поддержка**: [GitHub Issues](https://github.com/your-username/cez-hdo-sensor/issues)
