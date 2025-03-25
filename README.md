(Due to technical issues, the search service is temporarily unavailable.)

# Документация Hunyuan Portal

## 🌐 Основная информация

- **Название проекта**: Hunyuan Portal
- **Главный файл**: `hunyuan.py`
- **Репозиторий**: [https://github.com/Dedstate/Hunyuan-Portal.git](https://github.com/Dedstate/Hunyuan-Portal.git)
- **Тип проекта**: CLI/GUI интерфейс для работы с моделью Hunyuan T1

## 🚀 Быстрый старт

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Dedstate/Hunyuan-Portal.git
   cd Hunyuan-Portal
   ```

2. Установите зависимости (рекомендуется использовать Poetry):
   ```bash
   poetry install
   ```

3. Запустите интерактивный режим:
   ```bash
   poetry run python hunyuan.py chat
   ```

## 📦 Установка и настройка

### Альтернативные способы установки

1. **Глобальная установка**:
   ```bash
   pip install git+https://github.com/Dedstate/Hunyuan-Portal.git
   ```

2. **Установка для разработки**:
   ```bash
   git clone https://github.com/Dedstate/Hunyuan-Portal.git
   cd Hunyuan-Portal
   pip install -e .
   ```

### Конфигурация

Создайте файл `.env` в корне проекта для настройки:

```ini
HUNYUAN_URL = tencent/Hunyuan-T1
DEFAULT_MARKDOWN = true
THEME = dark
```

## 🖥️ Основные команды

### Запуск интерактивного чата

```bash
python hunyuan.py chat [опции]
```

Опции:

- `--url` - URL модели (по умолчанию `tencent/Hunyuan-T1`)
- `--gui` - запуск графического интерфейса
- `--theme` - цветовая тема (light/dark)

### Разовый запрос

```bash
python hunyuan.py ask "Ваш запрос" [опции]
```

Опции:

- `--file` - загрузить запрос из файла
- `--output` - сохранить ответ в файл

## 🔧 Примеры использования

1. Простой запрос:
   ```bash
   python hunyuan.py ask "Объясните теорию относительности"
   ```

2. Чтение запроса из файла:
   ```bash
   python hunyuan.py ask --file query.txt
   ```

3. Сохранение ответа:
   ```bash
   python hunyuan.py ask "Напишите код нейросети" --output network.py
   ```

4. Длительная беседа в GUI:
   ```bash
   python hunyuan.py chat --gui --theme dark
   ```

## 🛠️ Разработка

### Структура проекта

```
Hunyuan-Portal/
├── hunyuan.py       # Главный исполняемый файл
├── poetry.lock
├── pyproject.toml
├── README.md
└── .env.example
```

### Установка для разработки

```bash
git clone https://github.com/Dedstate/Hunyuan-Portal.git
cd Hunyuan-Portal
poetry install --with dev
```

### Тестирование

```bash
poetry run pytest
```

## 🤝 Поддержка и обратная связь

Для вопросов и предложений:

- [Issues на GitHub](https://github.com/Dedstate/Hunyuan-Portal/issues)
- Email: support@dedstate.com

## 🔄 Обновление

```bash
cd Hunyuan-Portal
git pull origin main
poetry install
```

## 📜 Лицензия

Проект распространяется под лицензией MIT. Подробнее см. в файле LICENSE.