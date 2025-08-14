# 🏠 Установка CEZ HDO Sensor в Home Assistant

## 📋 Способы установки

### 🔧 Способ 1: Через HACS (рекомендуется)

1. **Установите HACS** (если еще не установлен):
   - Перейдите на [hacs.xyz](https://hacs.xyz) и следуйте инструкциям

2. **Добавьте пользовательский репозиторий**:
   - Откройте HACS в Home Assistant
   - Перейдите в раздел "Integrations" 
   - Нажмите на три точки (⋮) в правом верхнем углу
   - Выберите "Custom repositories"
   - Добавьте URL: `https://github.com/your-username/cez-hdo-sensor`
   - Выберите категорию: "Integration"
   - Нажмите "ADD"

3. **Установите интеграцию**:
   - Найдите "CEZ HDO Sensor" в списке интеграций HACS
   - Нажмите "Download"
   - Перезапустите Home Assistant

### 📁 Способ 2: Ручная установка

1. **Скачайте архив** с GitHub:
   ```bash
   wget https://github.com/your-username/cez-hdo-sensor/archive/main.zip
   unzip main.zip
   ```

2. **Скопируйте файлы**:
   - Создайте папку `config/custom_components/cez_hdo/` в вашем Home Assistant
   - Скопируйте содержимое папки `cez_hdo/` в созданную папку

3. **Структура должна быть**:
   ```
   config/
   └── custom_components/
       └── cez_hdo/
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

4. **Перезапустите Home Assistant**

## ⚙️ Настройка интеграции

1. **Добавьте интеграцию**:
   - Перейдите в **Settings** → **Devices & Services**
   - Нажмите **Add Integration**
   - Найдите "CEZ HDO Sensor"

2. **Заполните настройки**:
   - **EAN код**: Введите EAN код вашего счетчика электроэнергии
   - **HDO сигнал**: Выберите один из доступных сигналов:
     - `a3b4dp01` - Стандартный HDO сигнал (по умолчанию)
     - `a3b4dp02` - Альтернативный HDO сигнал  
     - `a3b4dp06` - Специальный HDO сигнал

3. **Сохраните настройки**:
   - Нажмите **Submit**
   - Дождитесь проверки подключения

## 🔍 Где найти EAN код

EAN код можно найти:
- На счетчике электроэнергии (наклейка или дисплей)
- В договоре с поставщиком электроэнергии
- В личном кабинете на сайте ČEZ Distribuce
- В мобильном приложении ČEZ

## 📊 Использование

После успешной настройки будет создан бинарный сенсор:
```
binary_sensor.cez_hdo_[ваш_ean_код]
```

### Состояния сенсора:
- **ON** (🟢): Активен низкий тариф
- **OFF** (🔴): Обычный тариф  
- **Unavailable**: Нет подключения к API

### Атрибуты сенсора:
- `ean`: EAN код счетчика
- `signal`: Выбранный HDO сигнал
- `current_period`: Текущий период тарифа
- `next_switch`: Время следующего переключения
- `today_switches_count`: Количество переключений сегодня
- `switches_today`: Полное расписание на сегодня

## 🤖 Пример автоматизации

```yaml
automation:
  - alias: "Включить бойлер при низком тарифе"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_859182400123456789
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.water_heater
      - service: notify.mobile_app_your_phone
        data:
          message: "Включен низкий тариф - запущен бойлер"

  - alias: "Выключить бойлер при окончании низкого тарифа"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_859182400123456789
        to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.water_heater
      - service: notify.mobile_app_your_phone
        data:
          message: "Низкий тариф закончился - бойлер выключен"
```

## 🧪 Тестирование

Перед установкой можно протестировать работу с помощью скриптов:

```bash
# Загрузите тестовые скрипты
wget https://github.com/your-username/cez-hdo-sensor/raw/main/test_api.py

# Протестируйте с вашим EAN
python3 test_api.py ВАШ_EAN_КОД a3b4dp01
```

## ❗ Устранение неполадок

### Сенсор показывает "Unavailable"
1. Проверьте правильность EAN кода
2. Убедитесь в наличии интернет-соединения
3. Проверьте логи Home Assistant: **Settings** → **System** → **Logs**

### Данные не обновляются
1. Компонент обновляет данные каждый час
2. Проверьте доступность API ČEZ Distribuce
3. Попробуйте перезагрузить интеграцию: **Settings** → **Devices & Services** → **CEZ HDO Sensor** → **Reload**

### Неправильный HDO сигнал
1. Проверьте в договоре с поставщиком, какой сигнал используется
2. Удалите и заново добавьте интеграцию с правильным сигналом
3. Протестируйте разные сигналы с помощью тестового скрипта

## 🆘 Поддержка

Если возникли проблемы:
1. Создайте issue в [GitHub репозитории](https://github.com/your-username/cez-hdo-sensor/issues)
2. Приложите логи Home Assistant
3. Укажите версию Home Assistant и способ установки
