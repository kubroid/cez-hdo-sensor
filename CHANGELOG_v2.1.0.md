# 🔄 Обновление логики CEZ HDO Sensor v2.1.0

## 🚀 Новые возможности

### ⚡ Обновления каждую минуту
- **Проблема**: Сенсор не обновлялся при переключении HDO тарифа
- **Решение**: Состояние сенсора проверяется каждую минуту

### 📋 Кеширование расписания
- **Оптимизация**: Данные с CEZ API загружаются только раз в час
- **Преимущество**: Минимальная нагрузка на API CEZ
- **Надежность**: Сенсор работает даже при временных проблемах с API

### 🌐 Поддержка нового формата CEZ API
- **Обновлен парсер** для структуры `data.datum.casy[signal].casy`
- **Обратная совместимость** с предыдущими версиями
- **Лучшая обработка ошибок** и логирование

## 📊 Технические изменения

### Coordinator (coordinator.py):
```python
# Обновление состояния каждую минуту
update_interval=timedelta(minutes=1)

# Кеширование расписания на час
_schedule_update_interval = timedelta(hours=1)
```

### API (api.py):
```python
# Новый формат CEZ API
datum_data = data.get("data", {}).get("datum", {})
casy_data = datum_data.get("casy", [])

# Поиск нужного сигнала
for signal_entry in casy_data:
    if signal_entry.get("signal") == self.signal:
        time_ranges = signal_entry.get("casy", [])
```

### Binary Sensor (binary_sensor.py):
```python
# Новые атрибуты
attrs = {
    "signal": self.coordinator.signal,
    "schedule_last_update": "2025-08-14 15:30:00",
    "schedule_age_minutes": 25,
    "today_switches_count": 6,
    "switches_today": [...]
}
```

## 🔍 Новые атрибуты сенсора

| Атрибут | Описание | Пример |
|---------|----------|---------|
| `signal` | Используемый HDO сигнал | `a3b4dp01` |
| `schedule_last_update` | Время последнего обновления расписания | `2025-08-14 15:30:00` |
| `schedule_age_minutes` | Возраст расписания в минутах | `25` |
| `today_switches_count` | Количество переключений сегодня | `6` |
| `switches_today` | Список всех переключений | `[{time: "14:00", state: "low_tariff"}]` |

## 🚀 Преимущества нового подхода

### ✅ Точность:
- Сенсор переключается **ровно в момент** изменения тарифа
- Не нужно ждать следующего часового обновления

### ✅ Производительность:
- **1 запрос в час** к CEZ API вместо 24
- Снижена нагрузка на серверы CEZ
- Меньше вероятность блокировки

### ✅ Надежность:
- Работает даже при **временных проблемах** с CEZ API
- Кешированное расписание действует до конца дня
- Подробное логирование для диагностики

## 🔧 Логирование

Новая система логирования поможет диагностировать проблемы:

```
DEBUG: Updating schedule from CEZ API
DEBUG: Found signal 'a3b4dp01' in response  
DEBUG: Found 3 time ranges for signal 'a3b4dp01'
DEBUG: Time range 14:00-16:00: ON at 14:00, OFF at 16:00
DEBUG: Current HDO state: LOW TARIFF, Next switch: 16:00
```

## 📱 Мониторинг в Home Assistant

### Состояние интеграции:
```yaml
# Проверка возраста расписания
- condition: template
  value_template: "{{ state_attr('binary_sensor.cez_hdo_123456789012345678', 'schedule_age_minutes') < 120 }}"
```

### Автоматизация обновления:
```yaml
# Уведомление о старом расписании
automation:
  - alias: "CEZ HDO - Old Schedule Warning"
    trigger:
      - platform: template
        value_template: "{{ state_attr('binary_sensor.cez_hdo_123456789012345678', 'schedule_age_minutes') > 180 }}"
    action:
      - service: persistent_notification.create
        data:
          message: "CEZ HDO расписание не обновлялось более 3 часов"
```

## 🧪 Тестирование

Запустите тест для проверки новой логики:

```bash
cd /config/custom_components/cez_hdo/
python3 test_new_logic.py
```

Ожидаемый результат:
```
🚀 Testing CEZ HDO logic for EAN: 123456789012345678
📍 Update #1
🔄 Updating schedule from CEZ API
✅ Schedule updated successfully
📊 Current HDO state: LOW TARIFF
⏰ Next switch: 16:00

📍 Update #2  
📋 Using cached schedule data
📊 Current HDO state: LOW TARIFF
```

## 🔄 Обновление до v2.1.0

### Автоматически (HACS):
1. HACS покажет доступное обновление
2. Нажмите "Update"
3. Перезапустите Home Assistant

### Вручную:
1. Скачайте новую версию
2. Замените папку `custom_components/cez_hdo`
3. Перезапустите Home Assistant

**Настройки сохранятся**, перенастройка не требуется!

---

**Версия**: 2.1.0  
**Дата**: 2025-08-14  
**Совместимость**: Home Assistant 2023.1+
