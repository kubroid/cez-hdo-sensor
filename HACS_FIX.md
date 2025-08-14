# 🔧 Исправление проблемы HACS

## ❌ Проблема: "is not a valid add-on repository"

Эта ошибка означает, что HACS не может распознать репозиторий как Home Assistant Integration.

## ✅ Решение:

### 1. Обновите файлы в GitHub:

Замените эти файлы в вашем репозитории `https://github.com/kubroid/cez-hdo-sensor`:

#### `hacs.json` (в корне репозитория):
```json
{
  "name": "CEZ HDO Sensor",
  "hacs": "1.6.0",
  "domains": ["binary_sensor"],
  "country": ["CZ"],
  "homeassistant": "2023.1.0",
  "iot_class": "Cloud Polling",
  "config_flow": true,
  "documentation": "https://github.com/kubroid/cez-hdo-sensor",
  "issue_tracker": "https://github.com/kubroid/cez-hdo-sensor/issues",
  "codeowners": ["@kubroid"],
  "requirements": ["aiohttp>=3.8.0"],
  "version": "1.1.0"
}
```

#### `custom_components/cez_hdo/manifest.json`:
```json
{
  "domain": "cez_hdo",
  "name": "CEZ HDO Sensor",
  "documentation": "https://github.com/kubroid/cez-hdo-sensor",
  "issue_tracker": "https://github.com/kubroid/cez-hdo-sensor/issues",
  "dependencies": [],
  "codeowners": ["@kubroid"],
  "requirements": ["aiohttp>=3.8.0"],
  "config_flow": true,
  "version": "1.1.0",
  "iot_class": "cloud_polling"
}
```

### 2. Проверьте структуру репозитория:

```
kubroid/cez-hdo-sensor/
├── custom_components/
│   └── cez_hdo/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── binary_sensor.py
│       ├── coordinator.py
│       ├── api.py
│       ├── const.py
│       ├── strings.json
│       └── translations/
│           ├── en.json
│           ├── ru.json
│           └── cs.json
├── hacs.json
├── README.md
└── LICENSE
```

### 3. После обновления файлов:

1. **Коммитьте изменения**:
   ```bash
   git add hacs.json custom_components/cez_hdo/manifest.json
   git commit -m "Fix HACS compatibility - update hacs.json and manifest.json"
   git push origin main
   ```

2. **Создайте release**:
   - Перейдите в GitHub: `https://github.com/kubroid/cez-hdo-sensor/releases`
   - Нажмите "Create a new release"
   - Tag: `v1.1.0`
   - Title: `CEZ HDO Sensor v1.1.0`
   - Опубликуйте release

3. **Добавьте в HACS**:
   - HACS → Integrations → ⋮ → Custom repositories
   - URL: `https://github.com/kubroid/cez-hdo-sensor`
   - Category: **Integration** (не Add-on!)
   - Add

### 4. Альтернативный способ установки:

Если HACS все еще не работает, используйте ручную установку:

```bash
# В папке config вашего Home Assistant:
cd /config
wget https://github.com/kubroid/cez-hdo-sensor/archive/main.zip
unzip main.zip
cp -r cez-hdo-sensor-main/custom_components/cez_hdo custom_components/
rm -rf cez-hdo-sensor-main main.zip
```

### 5. Проверка в Home Assistant:

1. Перезапустите Home Assistant
2. Settings → Devices & Services → Add Integration
3. Найдите "CEZ HDO Sensor"
4. Если не видите - проверьте логи: Settings → System → Logs

## 🐛 Диагностика:

### Если все еще не работает:

1. **Проверьте логи HACS**:
   - Settings → System → Logs
   - Найдите ошибки HACS

2. **Проверьте файлы**:
   - `hacs.json` должен быть в корне репозитория
   - `manifest.json` должен быть в `custom_components/cez_hdo/`
   - Версии в обоих файлах должны совпадать

3. **Попробуйте другую категорию**:
   - При добавлении в HACS попробуйте "Integration" вместо "Plugin"

## 📝 Команды для быстрого исправления:

```bash
# Клонируйте обновленные файлы
cd /tmp
wget https://github.com/kubroid/cez-hdo-sensor/raw/main/hacs.json
wget https://github.com/kubroid/cez-hdo-sensor/raw/main/custom_components/cez_hdo/manifest.json

# Проверьте содержимое
cat hacs.json
cat manifest.json
```

После внесения изменений репозиторий должен быть распознан HACS как валидная интеграция! 🎯
