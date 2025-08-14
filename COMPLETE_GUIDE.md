# 📋 Полное руководство по установке CEZ HDO Sensor

## 🎯 Краткий обзор

**CEZ HDO Sensor** - это пользовательский компонент для Home Assistant, который мониторит HDO (Hromadné dálkové ovládání) сигналы от ČEZ Distribuce и показывает, когда активен низкий тариф на электроэнергию.

### ✨ Возможности:
- 🟢 Бинарный сенсор (ON = низкий тариф, OFF = обычный)
- 📡 Поддержка сигналов: a3b4dp01, a3b4dp02, a3b4dp06
- 🌐 Интерфейс на русском, английском, чешском
- 📅 Расписание переключений на сегодня
- ⏰ Время до следующего переключения

---

## 🚀 Установка в Home Assistant

### 📥 Способ 1: Через HACS (РЕКОМЕНДУЕТСЯ)

#### 1️⃣ Подготовка HACS
- Убедитесь, что HACS установлен ([инструкция](https://hacs.xyz))
- Если нет - установите его сначала

#### 2️⃣ Добавление репозитория
1. Откройте **HACS** в Home Assistant
2. Перейдите в **Integrations**
3. Нажмите **⋮** (три точки в правом верхнем углу)
4. Выберите **Custom repositories**
5. В поле **Repository** введите:
   ```
   https://github.com/your-username/cez-hdo-sensor
   ```
6. В **Category** выберите **Integration**
7. Нажмите **ADD**

#### 3️⃣ Установка
1. Найдите "CEZ HDO Sensor" в списке интеграций HACS
2. Нажмите на неё
3. Нажмите **Download**
4. Дождитесь завершения загрузки
5. **ПЕРЕЗАПУСТИТЕ HOME ASSISTANT**

#### 4️⃣ Настройка
1. Перейдите в **Settings** → **Devices & Services**
2. Нажмите **+ Add Integration**
3. Найдите и выберите "CEZ HDO Sensor"
4. Заполните форму:
   - **EAN Code**: Ваш EAN код счетчика (например: 859182400123456789)
   - **HDO Signal**: Выберите сигнал:
     - `a3b4dp01` - Стандартный (по умолчанию)
     - `a3b4dp02` - Альтернативный
     - `a3b4dp06` - Специальный
5. Нажмите **Submit**
6. Дождитесь проверки подключения

---

### 📁 Способ 2: Ручная установка

#### 1️⃣ Скачивание
```bash
# Вариант 1: wget
wget https://github.com/your-username/cez-hdo-sensor/archive/main.zip
unzip main.zip

# Вариант 2: git clone
git clone https://github.com/your-username/cez-hdo-sensor.git
```

#### 2️⃣ Копирование файлов
```bash
# Скопируйте папку компонента
cp -r cez-hdo-sensor-main/custom_components/cez_hdo /config/custom_components/

# Или создайте структуру вручную:
mkdir -p /config/custom_components/cez_hdo
```

#### 3️⃣ Проверка структуры
Убедитесь, что структура выглядит так:
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

#### 4️⃣ Перезапуск и настройка
1. **Перезапустите Home Assistant**
2. Настройте как в способе 1 (пункт 4️⃣)

---

## 📋 Что загружать в GitHub

### 🗂️ Структура репозитория:
```
cez-hdo-sensor/
├── custom_components/          # Обязательно
│   └── cez_hdo/               # Компонент
├── README.md                  # Описание
├── INSTALLATION.md            # Подробная инструкция  
├── QUICK_INSTALL.md           # Быстрая установка
├── LICENSE                    # Лицензия MIT
├── hacs.json                  # Конфигурация HACS
├── .gitignore                 # Исключения Git
└── tests/                     # Тесты (опционально)
    ├── test_api.py
    ├── test_real_data.py
    └── requirements.txt
```

### 📤 Пошаговая загрузка в GitHub:

#### 1️⃣ Создание репозитория
1. Перейдите на [github.com](https://github.com)
2. Нажмите "New repository"
3. **Repository name**: `cez-hdo-sensor`
4. **Description**: `CEZ HDO Sensor for Home Assistant - Monitor low tariff periods`
5. Выберите **Public**
6. НЕ добавляйте README, .gitignore, license (у нас есть свои)
7. Нажмите **Create repository**

#### 2️⃣ Загрузка файлов
```bash
# Распакуйте готовую структуру
tar -xzf cez_hdo_github_final.tar.gz -C cez-hdo-sensor/

# Перейдите в папку
cd cez-hdo-sensor

# Инициализируйте Git
git init
git add .
git commit -m "Initial release v1.1.0 - CEZ HDO Sensor with signal selection"

# Привяжите к GitHub (замените your-username)
git remote add origin https://github.com/your-username/cez-hdo-sensor.git
git branch -M main
git push -u origin main
```

#### 3️⃣ Создание релиза
1. В репозитории нажмите **Releases**
2. **Create a new release**
3. **Tag version**: `v1.1.0`
4. **Release title**: `CEZ HDO Sensor v1.1.0`
5. **Description**:
```markdown
## ✨ Features
- 🔌 Support for multiple HDO signals (a3b4dp01, a3b4dp02, a3b4dp06)
- 🌐 Multi-language support (English, Russian, Czech)
- ⚡ Real-time tariff monitoring
- ⚙️ Configurable via Home Assistant UI
- 📱 Binary sensor with detailed attributes

## 🔧 Installation
- Via HACS: Add custom repository `https://github.com/your-username/cez-hdo-sensor`
- Manual: Download and copy to `custom_components/cez_hdo/`

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

## 🧪 Compatibility
- Home Assistant 2023.1.0+
- Requires internet connection to ČEZ Distribuce API
- Tested with real CEZ API responses

## 🚀 Quick Start
1. Install via HACS or manually
2. Add integration: Settings → Devices & Services → Add Integration
3. Enter your EAN code and select HDO signal
4. Use sensor in automations: `binary_sensor.cez_hdo_[your_ean]`
```
6. **Publish release**

---

## 🎯 Использование после установки

### 📊 Сенсор
Будет создан: `binary_sensor.cez_hdo_[ваш_ean_код]`

**Состояния:**
- 🟢 **ON**: Низкий тариф активен
- 🔴 **OFF**: Обычный тариф
- ⚠️ **Unavailable**: Нет связи с API

**Атрибуты:**
- `ean`: EAN код счетчика
- `signal`: Выбранный HDO сигнал  
- `current_period`: Текущий период ("low_tariff"/"normal_tariff")
- `next_switch`: Время следующего переключения
- `today_switches_count`: Количество переключений сегодня
- `switches_today`: Полное расписание на день

### 🤖 Пример автоматизации
```yaml
automation:
  - alias: "Управление бойлером по HDO"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_859182400123456789
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: binary_sensor.cez_hdo_859182400123456789
                state: "on"
            sequence:
              - service: switch.turn_on
                target:
                  entity_id: switch.water_heater
              - service: notify.mobile_app_phone
                data:
                  message: "🟢 Включен низкий тариф - запущен бойлер"
          - conditions:
              - condition: state
                entity_id: binary_sensor.cez_hdo_859182400123456789
                state: "off"
            sequence:
              - service: switch.turn_off
                target:
                  entity_id: switch.water_heater
              - service: notify.mobile_app_phone
                data:
                  message: "🔴 Низкий тариф закончился - бойлер выключен"
```

---

## 🔍 Поиск EAN кода

EAN код можно найти:
1. **На счетчике** - наклейка или дисплей
2. **В договоре** с поставщиком электроэнергии  
3. **На сайте ČEZ** в личном кабинете
4. **В мобильном приложении** ČEZ
5. **В счетах** за электроэнергию

---

## ❗ Устранение неполадок

### Сенсор показывает "Unavailable"
1. ✅ Проверьте правильность EAN кода
2. 🌐 Убедитесь в наличии интернета
3. 📝 Проверьте логи: Settings → System → Logs

### Данные не обновляются
1. ⏰ Компонент обновляется каждый час
2. 🔌 Проверьте доступность API ČEZ
3. 🔄 Перезагрузите интеграцию: Settings → Devices & Services → CEZ HDO → Reload

### Неправильный HDO сигнал
1. 📋 Проверьте договор с поставщиком
2. 🧪 Протестируйте разные сигналы:
   ```bash
   python3 test_api.py ВАШ_EAN a3b4dp01
   python3 test_api.py ВАШ_EAN a3b4dp02  
   python3 test_api.py ВАШ_EAN a3b4dp06
   ```
3. 🔄 Удалите и заново добавьте интеграцию

### Тестирование перед установкой
```bash
# Скачайте тестовый скрипт
wget https://github.com/your-username/cez-hdo-sensor/raw/main/tests/test_api.py

# Протестируйте с вашим EAN
python3 test_api.py ВАШ_EAN_КОД a3b4dp01
```

---

## 🆘 Поддержка

**GitHub**: [Issues](https://github.com/your-username/cez-hdo-sensor/issues)
**Документация**: [README.md](https://github.com/your-username/cez-hdo-sensor)
**Быстрая помощь**: [QUICK_INSTALL.md](https://github.com/your-username/cez-hdo-sensor/blob/main/QUICK_INSTALL.md)

При создании issue приложите:
- Версию Home Assistant
- Логи из Settings → System → Logs
- EAN код (можно замаскировать: 859182400608******)
- Выбранный HDO сигнал
