# 📂 Подготовка для загрузки в GitHub

## 🚀 Что загружать в GitHub репозиторий

### 📁 Структура репозитория:

```
cez-hdo-sensor/
├── custom_components/
│   └── cez_hdo/
│       ├── __init__.py
│       ├── api.py
│       ├── binary_sensor.py
│       ├── config_flow.py
│       ├── const.py
│       ├── coordinator.py
│       ├── manifest.json
│       ├── strings.json
│       └── translations/
│           ├── cs.json
│           ├── en.json
│           └── ru.json
├── README.md
├── INSTALLATION.md
├── LICENSE
├── hacs.json
└── tests/ (опционально)
    ├── test_api.py
    ├── test_real_data.py
    └── requirements.txt
```

### 📋 Обязательные файлы для HACS:

1. **hacs.json** - Конфигурация для HACS ✅
2. **custom_components/cez_hdo/** - Папка с компонентом ✅
3. **README.md** - Описание проекта ✅
4. **LICENSE** - Лицензия ✅

### 📝 Пошаговая инструкция:

#### 1. Создайте репозиторий на GitHub
- Перейдите на [github.com](https://github.com)
- Нажмите "New repository"
- Название: `cez-hdo-sensor`
- Описание: `CEZ HDO Sensor for Home Assistant`
- Установите Public
- НЕ добавляйте README, .gitignore, license (загрузим свои)

#### 2. Загрузите файлы
```bash
# Клонируйте пустой репозиторий
git clone https://github.com/your-username/cez-hdo-sensor.git
cd cez-hdo-sensor

# Скопируйте файлы из нашего проекта
mkdir -p custom_components
cp -r "/path/to/cez_hdo" custom_components/
cp "/path/to/README.md" .
cp "/path/to/INSTALLATION.md" .
cp "/path/to/LICENSE" .
cp "/path/to/hacs.json" .

# Опционально: тесты
mkdir tests
cp "/path/to/test_*.py" tests/

# Загрузите в GitHub
git add .
git commit -m "Initial release v1.1.0 - CEZ HDO Sensor with signal selection"
git push origin main
```

#### 3. Создайте release
- В GitHub репозитории нажмите "Releases"
- Нажмите "Create a new release"
- Tag: `v1.1.0`
- Title: `CEZ HDO Sensor v1.1.0`
- Описание:
```markdown
## ✨ Features
- Support for multiple HDO signals (a3b4dp01, a3b4dp02, a3b4dp06)
- Multi-language support (English, Russian, Czech)
- Real-time tariff monitoring
- Configurable via Home Assistant UI

## 🔧 Installation
See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

## 🧪 Compatibility
- Home Assistant 2023.1.0+
- Requires internet connection to ČEZ Distribuce API
```

#### 4. Добавьте в HACS Community Store (опционально)
- Создайте PR в [HACS-default](https://github.com/hacs/default)
- Или пользователи могут добавить как custom repository

## 🔗 URL для пользователей

После загрузки дайте пользователям эти ссылки:

### Для HACS:
```
https://github.com/your-username/cez-hdo-sensor
```

### Для скачивания:
```
https://github.com/your-username/cez-hdo-sensor/archive/main.zip
```

### Документация:
```
https://github.com/your-username/cez-hdo-sensor/blob/main/INSTALLATION.md
```

## ✅ Проверочный список перед загрузкой:

- [ ] Все файлы компонента в папке `custom_components/cez_hdo/`
- [ ] hacs.json содержит правильную конфигурацию
- [ ] README.md описывает функциональность
- [ ] INSTALLATION.md содержит инструкции по установке
- [ ] LICENSE файл присутствует
- [ ] Версия в manifest.json соответствует hacs.json
- [ ] Тесты работают корректно
- [ ] Переводы на всех языках

## 🔄 Обновления

Для выпуска обновлений:

1. Обновите версию в `manifest.json` и `hacs.json`
2. Создайте новый коммит: `git commit -m "Release v1.2.0"`
3. Создайте новый tag: `git tag v1.2.0`
4. Загрузите: `git push origin main --tags`
5. Создайте новый release на GitHub
