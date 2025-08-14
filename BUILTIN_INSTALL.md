# 🚀 Быстрая установка - Встроенная интеграция

## 📦 Скачать и установить за 3 минуты

### ✅ Способ 1: Прямая ссылка
```bash
# Скачать архив ветки builtin-integration
wget https://github.com/kubroid/cez-hdo-sensor/archive/builtin-integration.zip

# Распаковать в нужную папку
unzip builtin-integration.zip
mv cez-hdo-sensor-builtin-integration/custom_components/cez_hdo /config/custom_components/

# Очистить временные файлы
rm -rf cez-hdo-sensor-builtin-integration builtin-integration.zip
```

### ✅ Способ 2: Через Git
```bash
# Клонировать только нужную ветку
git clone -b builtin-integration https://github.com/kubroid/cez-hdo-sensor.git

# Скопировать интеграцию
cp -r cez-hdo-sensor/custom_components/cez_hdo /config/custom_components/

# Удалить временную папку
rm -rf cez-hdo-sensor
```

### ✅ Способ 3: Ручное скачивание
1. Идите на https://github.com/kubroid/cez-hdo-sensor/tree/builtin-integration
2. Нажмите **Code** → **Download ZIP**
3. Распакуйте архив
4. Скопируйте папку `custom_components/cez_hdo` в `/config/custom_components/`

## 🔧 Проверка установки

После копирования должна быть такая структура:
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

## ⚡ Завершение установки

1. **Перезапустите** Home Assistant
2. Перейдите в **Settings** → **Devices & Services**
3. Нажмите **Add Integration**
4. Найдите **"CEZ HDO Sensor"**
5. Введите ваш EAN и выберите сигнал
6. Готово! 🎉

## 🆚 Преимущества этой версии

- ✅ **Без HACS**: Не нужен HACS для установки
- ✅ **Стабильная**: Не зависит от внешних репозиториев
- ✅ **Простая**: Скопировал папку - работает
- ✅ **Быстрая**: Установка за 2-3 минуты

## 🔄 Обновление

Для обновления повторите процесс установки - скачайте новую версию и замените папку.

---

**Ветка**: `builtin-integration` | **Версия**: 2.0.0
