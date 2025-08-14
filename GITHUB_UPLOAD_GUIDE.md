# 🚀 Загрузка на GitHub - Финальные шаги

## 📤 1. Загрузка веток

```bash
cd "/home/alex/Documents/home assistant/HDO sensor/github_ready"

# Загружаем master ветку (HACS версия)
git checkout master
git push origin master

# Загружаем builtin-integration ветку (встроенная версия)  
git checkout builtin-integration
git push origin builtin-integration
```

## 🏷️ 2. Создание релизов

### Релиз для HACS версии (master):
1. Идите на https://github.com/kubroid/cez-hdo-sensor
2. Переключитесь на ветку **master**
3. Нажмите **Releases** → **Create a new release**
4. Заполните:
   - **Tag**: `v1.1.0`
   - **Title**: `CEZ HDO Sensor v1.1.0 - HACS Integration`
   - **Description**: 
   ```markdown
   ## 🏆 HACS версия интеграции
   
   ### ✨ Функции:
   - 📡 Поддержка сигналов a3b4dp01, a3b4dp02, a3b4dp06
   - 🔄 Автообновления через HACS
   - 🌐 Многоязычность (ru, en, cs)
   - ⚡ Мониторинг HDO тарифов в реальном времени
   
   ### 📦 Установка:
   - Через HACS: добавьте репозиторий как Custom Integration
   - Категория: Integration
   - URL: https://github.com/kubroid/cez-hdo-sensor
   
   ### 📖 Документация:
   - [Инструкция по HACS](HACS_CRITICAL_FIX.md)
   - [Исправление ошибок](QUICK_FIX_ADD_ON_ERROR.md)
   - [Контрольный список](CHECKLIST.md)
   ```

### Релиз для встроенной версии (builtin-integration):
1. Переключитесь на ветку **builtin-integration**
2. Нажмите **Releases** → **Create a new release**
3. Заполните:
   - **Tag**: `v2.0.0`
   - **Title**: `CEZ HDO Sensor v2.0.0 - Standalone Integration`
   - **Description**:
   ```markdown
   ## 🏠 Встроенная версия интеграции
   
   ### ✨ Функции:
   - 🚀 Простая установка без HACS
   - 📡 Поддержка сигналов a3b4dp01, a3b4dp02, a3b4dp06
   - 🛡️ Стабильная работа без зависимостей
   - 🌐 Многоязычность (ru, en, cs)
   
   ### 📦 Быстрая установка:
   ```bash
   wget https://github.com/kubroid/cez-hdo-sensor/archive/builtin-integration.zip
   unzip builtin-integration.zip
   cp -r cez-hdo-sensor-builtin-integration/custom_components/cez_hdo /config/custom_components/
   ```
   
   ### 📖 Документация:
   - [Инструкция по установке](BUILTIN_INSTALL.md)
   - [Сравнение версий](VERSION_COMPARISON.md)
   - [Обзор веток](BRANCHES_OVERVIEW.md)
   ```

## 🔧 3. Обновление главной страницы

В README на главной странице GitHub добавьте выбор версии:

```markdown
# CEZ HDO Sensor для Home Assistant

## 🎯 Выберите версию:

### 🏆 [HACS версия](https://github.com/kubroid/cez-hdo-sensor/tree/master) 
**Рекомендуется для опытных пользователей**
- Автообновления через HACS
- Простая установка в 1 клик
- [Инструкция установки](HACS_CRITICAL_FIX.md)

### 🏠 [Встроенная версия](https://github.com/kubroid/cez-hdo-sensor/tree/builtin-integration)
**Рекомендуется для всех пользователей**  
- Простая установка без HACS
- Стабильная работа
- [Инструкция установки](BUILTIN_INSTALL.md)

[📊 Сравнение версий](VERSION_COMPARISON.md)
```

## ✅ 4. Проверка готовности

После загрузки проверьте:

### HACS версия:
- [ ] Ветка `master` загружена
- [ ] Релиз `v1.1.0` создан
- [ ] `hacs.json` присутствует
- [ ] Документация HACS готова

### Встроенная версия:
- [ ] Ветка `builtin-integration` загружена  
- [ ] Релиз `v2.0.0` создан
- [ ] `hacs.json` отсутствует
- [ ] Документация установки готова

## 🎉 Готово!

После выполнения всех шагов у вас будет:
- 🏆 **HACS интеграция** в ветке master
- 🏠 **Встроенная интеграция** в ветке builtin-integration
- 📖 **Полная документация** для обеих версий
- 🚀 **Готовые релизы** для скачивания

**Проект полностью готов к использованию!** 🎉
