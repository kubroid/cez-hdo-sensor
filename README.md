# CEZ HDO Sensor - Встроенная интеграция

[![GitHub release](https://img.shields.io/github/release/kubroid/cez-hdo-sensor.svg)](https://github.com/kubroid/cez-hdo-sensor/releases)

🏠 **Встроенная версия** CEZ HDO Sensor для Home Assistant - работает без HACS и дополнительных зависимостей!

## ✨ Особенности

- 📡 **Поддержка сигналов**: a3b4dp01, a3b4dp02, a3b4dp06
- ⚡ **Обновления каждую минуту**: Мгновенное переключение HDO без задержек
- � **Умное кеширование**: Расписание обновляется раз в час, состояние - каждую минуту
- �🚀 **Простая установка**: Скопировать папку и перезапустить
- 🔧 **Без зависимостей**: Не нужен HACS или Docker
- 🌐 **Многоязычность**: Русский, английский, чешский
- 🛡️ **Стабильность**: Работает даже при проблемах с CEZ API
- 📊 **Мониторинг**: Отслеживание возраста расписания и диагностика

## 📦 Установка

### 🚀 Быстрая установка

1. **Скачайте архив**: [Скачать ZIP](https://github.com/kubroid/cez-hdo-sensor/archive/builtin-integration.zip)
2. **Распакуйте** в папку `/config/custom_components/`
3. **Перезапустите** Home Assistant
4. **Добавьте интеграцию**: Settings → Devices & Services → Add Integration → "CEZ HDO Sensor"

### 📁 Ручная установка

```bash
# В папке config Home Assistant:
cd /config/custom_components/
wget https://github.com/kubroid/cez-hdo-sensor/archive/builtin-integration.zip
unzip builtin-integration.zip
mv cez-hdo-sensor-builtin-integration/custom_components/cez_hdo .
rm -rf cez-hdo-sensor-builtin-integration builtin-integration.zip

# Перезапустите Home Assistant
```

### � Структура файлов

После установки должна быть такая структура:
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

## ⚙️ Настройка

1. Перейдите в **Settings** → **Devices & Services**
2. Нажмите **Add Integration**
3. Найдите **"CEZ HDO Sensor"**
4. Введите ваш **EAN код** счетчика
5. Выберите **HDO сигнал** (по умолчанию a3b4dp01)
6. Нажмите **Submit**

## 📊 Что создается

После настройки будет создан бинарный сенсор:
- **Название**: `binary_sensor.cez_hdo_[ваш_ean]`
- **Состояния**:
  - `ON` - Активен низкий тариф (HDO включен)
  - `OFF` - Обычный тариф (HDO выключен)

### 📋 Атрибуты сенсора

- `ean` - EAN код счетчика
- `signal` - Используемый HDO сигнал
- `current_period` - Текущий период (low_tariff/normal_tariff)
- `next_switch` - Время следующего переключения
- `schedule_last_update` - Время последнего обновления расписания
- `schedule_age_minutes` - Возраст расписания в минутах
- `today_switches_count` - Количество переключений сегодня
- `switches_today` - Подробное расписание на день
## 🔄 Использование в автоматизациях

```yaml
automation:
  - alias: "Включить бойлер при дешевом тарифе"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_123456789012345678
        to: 'on'
    action:
      - service: switch.turn_on
        entity_id: switch.water_heater

  - alias: "Выключить бойлер при дорогом тарифе"
    trigger:
      - platform: state
        entity_id: binary_sensor.cez_hdo_123456789012345678
        to: 'off'
    action:
      - service: switch.turn_off
        entity_id: switch.water_heater
```

## 📊 Мониторинг и диагностика

### Проверка состояния интеграции:
```yaml
# Автоматизация для уведомления о старом расписании
automation:
  - alias: "CEZ HDO - Предупреждение о старом расписании"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('binary_sensor.cez_hdo_123456789012345678', 'schedule_age_minutes') > 180 }}
    action:
      - service: persistent_notification.create
        data:
          message: "CEZ HDO: Расписание не обновлялось более 3 часов"
```

### Карточка для мониторинга:
```yaml
type: entities
title: CEZ HDO Статус
entities:
  - entity: binary_sensor.cez_hdo_123456789012345678
    name: Низкий тариф
  - type: attribute
    entity: binary_sensor.cez_hdo_123456789012345678
    attribute: next_switch
    name: Следующее переключение
  - type: attribute
    entity: binary_sensor.cez_hdo_123456789012345678
    attribute: schedule_age_minutes
    name: Возраст расписания (мин)
  - type: attribute
    entity: binary_sensor.cez_hdo_123456789012345678
    attribute: today_switches_count
    name: Переключений сегодня
```

## 🌍 Поддерживаемые языки

- 🇷🇺 **Русский** (ru)
- 🇺🇸 **English** (en) 
- 🇨🇿 **Čeština** (cs)

## 🛠️ Технические детали

- **Обновление состояния**: Каждую минуту
- **Обновление расписания**: Каждый час
- **API**: ČEZ Distribuce WebAPI
- **Зависимости**: Только `aiohttp`
- **Совместимость**: Home Assistant 2023.1+
- **Версия**: 2.1.0

## 🆚 Отличия от HACS версии

| Особенность | HACS версия | Встроенная версия |
|-------------|-------------|-------------------|
| Установка | Через HACS | Копирование папки |
| Обновления | Автоматические | Ручные |
| Зависимости | HACS | Нет |
| Обновление состояния | Каждый час | **Каждую минуту** |
| Кеширование | Нет | **Умное (1 час)** |
| Сложность | Средняя | Простая |
| Стабильность | Высокая | **Очень высокая** |
| Мониторинг | Базовый | **Расширенный** |

## ❓ Часто задаваемые вопросы

### Где найти EAN код?
EAN код указан на вашем счетчике электроэнергии или в договоре с поставщиком.

### Какой HDO сигнал выбрать?
- `a3b4dp01` - основной сигнал (по умолчанию)
- `a3b4dp02` - альтернативный сигнал
- `a3b4dp06` - специальный сигнал

### Не работает интеграция?
1. Проверьте правильность EAN кода
2. Убедитесь что интернет подключение работает
3. Посмотрите логи в Settings → System → Logs

## 🐛 Сообщить об ошибке

Если нашли ошибку, создайте [issue на GitHub](https://github.com/kubroid/cez-hdo-sensor/issues) с подробным описанием проблемы.

## 📜 Лицензия

MIT License - используйте свободно!

---

**Версия для ветки**: `builtin-integration` v2.1.0  
**Основная ветка**: `main` (HACS версия) v1.1.0  
**Новое**: Умное кеширование + обновления каждую минуту 🚀

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
