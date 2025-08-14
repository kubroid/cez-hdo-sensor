# 🚨 КРИТИЧЕСКИ ВАЖНО для работы с HACS!

## ❌ Почему HACS не видит репозиторий:

HACS требует **обязательный РЕЛИЗ (release)** с тегом в GitHub!

## ✅ Пошаговое решение:

### 1. 📤 Загрузите обновленные файлы в GitHub:

```bash
# Загрузите эти исправленные файлы:
git add .
git commit -m "Fix HACS integration support"
git push origin main
```

### 2. 🏷️ Создайте релиз в GitHub (ОБЯЗАТЕЛЬНО!):

1. Перейдите в ваш репозиторий: https://github.com/kubroid/cez-hdo-sensor
2. Нажмите **"Releases"** (справа на странице)
3. Нажмите **"Create a new release"**
4. Заполните:
   - **Tag version**: `v1.1.0` (обязательно начинать с 'v')
   - **Release title**: `CEZ HDO Sensor v1.1.0`
   - **Description**:
   ```markdown
   ## ✨ Первый релиз CEZ HDO Sensor
   
   ### Функции:
   - 📡 Поддержка сигналов a3b4dp01, a3b4dp02, a3b4dp06
   - 🌐 Многоязычность (русский, английский, чешский)
   - ⚡ Мониторинг HDO тарифов в реальном времени
   - 🔧 Простая настройка через UI
   
   ### Установка:
   - Через HACS: добавьте репозиторий как Custom Integration
   - Вручную: скопируйте папку в custom_components
   ```
5. Нажмите **"Publish release"**

### 3. 🔄 Добавьте в HACS (после создания релиза!):

1. В Home Assistant откройте **HACS → Integrations**
2. Нажмите **⋮** (три точки) → **Custom repositories**
3. **Repository**: `https://github.com/kubroid/cez-hdo-sensor`
4. **Category**: **Integration** (НЕ Add-on!)
5. Нажмите **"ADD"**
6. Найдите "CEZ HDO Sensor" и установите

### 4. ⚠️ Если все еще не работает:

#### Проверьте в браузере:
- https://github.com/kubroid/cez-hdo-sensor/releases (должен быть релиз)
- https://raw.githubusercontent.com/kubroid/cez-hdo-sensor/main/hacs.json (должен открываться)
- https://raw.githubusercontent.com/kubroid/cez-hdo-sensor/main/custom_components/cez_hdo/manifest.json (должен открываться)

#### Альтернативный способ добавления:
1. В HACS попробуйте разные категории:
   - Integration ✅
   - Plugin ❌
   - Theme ❌
2. Убедитесь, что URL точный: `https://github.com/kubroid/cez-hdo-sensor`

### 5. 📁 Ручная установка (если HACS не работает):

```bash
# В папке config Home Assistant:
cd /config/custom_components
wget https://github.com/kubroid/cez-hdo-sensor/archive/v1.1.0.zip
unzip v1.1.0.zip
mv cez-hdo-sensor-1.1.0/custom_components/cez_hdo .
rm -rf cez-hdo-sensor-1.1.0 v1.1.0.zip
```

## 🎯 Главное:

**БЕЗ РЕЛИЗА HACS НЕ БУДЕТ РАБОТАТЬ!**

После создания релиза с тегом `v1.1.0` HACS должен найти интеграцию.

## 🔍 Проверка корректности:

После всех действий проверьте:
- [ ] Релиз создан с тегом v1.1.0
- [ ] hacs.json доступен по ссылке
- [ ] manifest.json доступен по ссылке  
- [ ] В HACS выбрана категория "Integration"
- [ ] URL точный без лишних символов
