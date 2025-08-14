# 🚨 БЫСТРОЕ ИСПРАВЛЕНИЕ: "not a valid add-on repository"

## Проблема:
Вы видите ошибку "not a valid add-on repository" при попытке добавить CEZ HDO Sensor

## Причина:
Вы добавляете репозиторий в **неправильном месте**!

## ✅ РЕШЕНИЕ:

### ❌ НЕ ЗДЕСЬ:
```
Настройки → Дополнения → Магазин дополнений → ⋮ → Репозитории
```

### ✅ А ЗДЕСЬ:
```
HACS → Integrations → ⋮ → Custom repositories
```

## 📝 Пошагово:

1. **Откройте HACS** (в боковом меню Home Assistant)
2. **Нажмите "Integrations"** (вкладка сверху)
3. **Нажмите ⋮** (три точки справа вверху)
4. **Выберите "Custom repositories"**
5. **Заполните**:
   - Repository: `https://github.com/kubroid/cez-hdo-sensor`
   - Category: **Integration** (не Add-on!)
6. **Нажмите "ADD"**

## 🎯 Главное:

**CEZ HDO Sensor** - это **Integration** для HACS, НЕ Add-on для Supervisor!

- ✅ **HACS → Integrations** (для пользовательских интеграций)
- ❌ **Настройки → Дополнения** (для системных дополнений)

## 🔧 Если все еще не работает:

1. Убедитесь что создан **релиз v1.1.0** в GitHub
2. Проверьте что репозиторий **публичный**
3. Попробуйте **перезагрузить** Home Assistant
4. Попробуйте **обновить** HACS

## 💡 Подсказка:

Если видите список "Node.js", "Python", "Home Assistant" в магазине дополнений - вы в **неправильном месте**! Это Supervisor Add-ons, а вам нужен HACS!
