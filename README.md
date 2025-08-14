# CEZ HDO Sensor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/kubroid/cez-hdo-sensor.svg)](https://github.com/kubroid/cez-hdo-sensor/releases)

Этот пользовательский компонент для Home Assistant позволяет мониторить состояние HDO (Hromadné dálkové ovládání) сигналов от ČEZ Distribuce. Компонент создает бинарный сенсор, который показывает, активен ли сейчас низкий тариф.

## Особенности

- **Бинарный сенсор**: Показывает состояние ON когда активен низкий тариф, OFF когда обычный тариф
- **Настраиваемый EAN**: Возможность указать свой EAN код счетчика
- **Выбор HDO сигнала**: Поддержка сигналов a3b4dp01, a3b4dp02, a3b4dp06
- **Автоматическое обновление**: Данные обновляются каждый час
- **Дополнительные атрибуты**: Время следующего переключения, расписание на сегодня
- **Простая настройка**: Настройка через UI Home Assistant
- **Многоязычность**: Поддержка русского, английского и чешского языков

## 📦 Установка

### 🏆 Через HACS (рекомендуется)

⚠️ **КРИТИЧЕСКИ ВАЖНО**: Добавляйте как **Integration**, НЕ как Add-on!

1. Откройте **HACS** в Home Assistant (боковое меню)
2. Перейдите во вкладку **"Integrations"**
3. Нажмите **⋮** (три точки справа вверху) → **"Custom repositories"**
4. Добавьте URL: `https://github.com/kubroid/cez-hdo-sensor`
5. Категория: **Integration** (НЕ Add-on!)
6. Найдите "CEZ HDO Sensor" в списке и установите

🚨 **Если видите ошибку "not a valid add-on repository"** - читайте [QUICK_FIX_ADD_ON_ERROR.md](QUICK_FIX_ADD_ON_ERROR.md)

### 📁 Ручная установка

1. Скопируйте папку `cez_hdo` в директорию `custom_components` вашего Home Assistant
2. Перезапустите Home Assistant

## Настройка

1. Перейдите в **Settings** → **Devices & Services**
2. Нажмите **Add Integration**
3. Найдите "CEZ HDO Sensor"
4. Введите ваш EAN код счетчика
5. Выберите HDO сигнал (по умолчанию a3b4dp01)
6. Нажмите **Submit**

## Использование

После настройки будет создан бинарный сенсор с именем `binary_sensor.cez_hdo_[ваш_ean]`.

### Состояния сенсора

- **ON**: Активен низкий тариф (HDO сигнал включен)
- **OFF**: Обычный тариф (HDO сигнал выключен)
- **Unavailable**: Нет связи с API или ошибка получения данных

### Атрибуты сенсора

- `ean`: EAN код вашего счетчика
- `signal`: HDO сигнал (a3b4dp01, a3b4dp02, или a3b4dp06)
- `current_period`: Текущий период ("low_tariff" или "normal_tariff")
- `next_switch`: Время следующего переключения тарифа
- `today_switches_count`: Количество переключений сегодня
- `switches_today`: Список всех переключений на сегодня с временем и состоянием

## Автоматизации

Пример автоматизации для включения устройств при низком тарифе:

```yaml
automation:
  - alias: "Turn on water heater during low tariff"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_123456789012345678
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.water_heater

  - alias: "Turn off water heater when low tariff ends"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_123456789012345678
        to: "off"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.water_heater
```

## Тестирование

Перед установкой можете протестировать API с помощью включенных тестовых скриптов:

```bash
# Тест с демонстрационными данными
python3 test_real_data.py

# Простой тест с вашим EAN и сигналом
python3 test_api.py ВАШ_EAN_КОД a3b4dp01

# Расширенный тест с таблицами
python3 test_api_extended.py ВАШ_EAN_КОД
```

Подробности в файле [TESTS.md](TESTS.md).

## Получение EAN кода

EAN код можно найти:
1. На вашем счетчике электроэнергии
2. В договоре с поставщиком электроэнергии
3. На сайте ČEZ Distribuce в личном кабинете

## HDO сигналы

Компонент поддерживает следующие HDO сигналы:
- **a3b4dp01**: Стандартный HDO сигнал (по умолчанию)
- **a3b4dp02**: Альтернативный HDO сигнал
- **a3b4dp06**: Специальный HDO сигнал с другим расписанием

Выберите сигнал, который соответствует вашему договору с поставщиком электроэнергии.

## Устранение неполадок

### Сенсор показывает "Unavailable"

1. Проверьте правильность EAN кода
2. Убедитесь, что есть интернет-соединение
3. Проверьте логи Home Assistant на наличие ошибок

### Данные не обновляются

1. Компонент обновляет данные каждый час
2. Проверьте доступность API ČEZ Distribuce
3. Перезапустите Home Assistant

## Поддержка

Если у вас есть вопросы или проблемы, создайте issue в GitHub репозитории.

## Лицензия

Этот проект распространяется под лицензией MIT.
