# 🤖 MCP AI Assistant

[![CI](https://github.com/Artem-Kornilov-pro/mcp-ai-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/Artem-Kornilov-pro/mcp-ai-assistant/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

🇷🇺 Русский | [🇬🇧 English](README.en.md)

**Персональный AI-ассистент с MCP-архитектурой, способный управлять файлами, GitHub и Google Sheets через естественный язык.**

---

## 🎯 Что это?

MCP AI Assistant — это терминальный AI-помощник, который не просто отвечает на вопросы, а **совершает действия** в реальном мире. Он умеет читать и писать файлы, управлять GitHub-репозиториями, создавать issues и pull requests, работать с Google Sheets — и всё это через обычный диалог.

Проект построен на **Model Context Protocol (MCP)** — открытом стандарте для подключения AI-моделей к внешним инструментам.

---

## 🧠 Как это работает

```
Пользователь → Терминал → LLM (DeepSeek) → MCP Server → Внешний сервис
                                                  ├── Файловая система
                                                  ├── GitHub API
                                                  └── Google Sheets API
```

1. Вы пишете запрос на естественном языке
2. LLM анализирует запрос и решает, какие инструменты нужны
3. MCP-сервер выполняет вызов API
4. Результат возвращается в диалог

---

## 🛠 Возможности (115 инструментов)

<details>
<summary><strong>📁 Файловая система (4)</strong></summary>

- **read_file** — чтение любого файла в рабочей директории
- **write_file** — создание или перезапись файла
- **list_directory** — список файлов и папок
- **search_files** — рекурсивный поиск по маске (например, `*.py`)
- 🔒 **Sandbox-безопасность** — нельзя выйти за пределы `WORKSPACE_DIR`
</details>

<details>
<summary><strong>🐙 GitHub (17)</strong></summary>

- **Репозитории**: list_repos, get_repo_info, create_repo
- **Файлы**: get_file, list_directory, create_or_update_file (с коммитом)
- **Issues**: create_issue, list_issues, update_issue (включая закрытие)
- **Pull Requests**: create_pull_request, list_pull_requests, merge_pull_request (merge/squash/rebase)
- **Ветки**: list_branches, create_branch
- **Коммиты**: list_commits
- **Поиск**: search_code, search_repos
</details>

<details>
<summary><strong>📊 Google Sheets (3)</strong></summary>

- **create_sheet** — создание таблицы в вашем Google-аккаунте
- **read_sheet** — чтение данных по ID с указанием диапазона
- **write_sheet** — запись значений в ячейки
- 🔑 Авторизация через личный OAuth-токен
</details>

<details>
<summary><strong>🌤 Погода (8)</strong></summary>

- **get_weather** — текущая погода: температура, ветер, влажность
- **get_temperature** — температура в °C с ощущением
- **get_forecast** — прогноз на 1-3 дня в °C
- **get_wind** — скорость и направление ветра
- **get_humidity** — влажность в процентах
- **get_astronomy** — рассвет, закат, фаза луны
- **get_weather_ascii** — визуальный ASCII-чарт погоды
- **compare_weather** — сравнение погоды двух городов
- 🌍 API wttr.in — без токена, без регистрации
</details>

<details>
<summary><strong>📅 Дата и время (8)</strong></summary>

- **get_current_time** — дата, время, день недели, неделя года
- **calculate_date** — прибавить/вычесть дни от даты
- **days_between** — разница в днях между датами
- **get_day_of_week** — день недели для даты
- **get_week_number** — номер недели по ISO
- **format_date_ru** — формат "12 июня 2026 года"
- **days_until** — сколько дней осталось/прошло
- **is_weekend** — проверка на выходной
</details>

<details>
<summary><strong>🗄 SQLite (3)</strong></summary>

- **execute_query** — выполнить SELECT-запрос
- **execute_statement** — выполнить INSERT/UPDATE/DELETE/CREATE
- **list_tables** — список всех таблиц в базе
- 💾 База хранится в `WORKSPACE_DIR/assistant.db`
</details>

<details>
<summary><strong>📊 Excel (4)</strong></summary>

- **read_excel** — чтение данных из .xlsx файла с указанием листа
- **write_excel** — запись данных в .xlsx (создание нового или дополнение существующего)
- **list_sheets** — список всех листов в Excel-файле
- **csv_to_excel** — конвертация CSV в формат Excel
</details>

<details>
<summary><strong>📋 CSV (3)</strong></summary>

- **read_csv** — чтение CSV-файла с настраиваемым лимитом строк
- **write_csv** — запись данных в CSV-файл
- **csv_to_json** — конвертация CSV в JSON-массив объектов
</details>

<details>
<summary><strong>📄 PDF (3)</strong></summary>

- **read_pdf** — извлечение текста из PDF (PyMuPDF, полный Unicode)
- **pdf_info** — метаданные: количество страниц, размер, автор, заголовок
- **create_pdf** — создание PDF с поддержкой кириллицы (Arial/DejaVu)
- 🔤 Полная поддержка русского текста при создании и чтении
</details>

<details>
<summary><strong>🗜 Архив (3)</strong></summary>

- **zip_files** — упаковка одного или нескольких файлов в ZIP-архив
- **unzip_file** — распаковка ZIP-архива в директорию
- **list_archive** — список файлов в архиве с их размерами
</details>

<details>
<summary><strong>🔤 Текст (5)</strong></summary>

- **hash_text** — хеш строки (md5/sha1/sha256)
- **encode_base64** / **decode_base64** — кодирование и декодирование base64
- **generate_uuid** — генерация случайного UUID4
- **word_count** — подсчёт слов, символов и строк в тексте
</details>

<details>
<summary><strong>🎲 Случайные числа (5)</strong></summary>

- **random_int** — случайное целое число в диапазоне
- **random_float** — случайное число с плавающей точкой в диапазоне
- **random_choice** — случайный элемент из списка
- **shuffle_list** — перемешать список
- **random_sample** — N уникальных случайных элементов из списка
</details>

<details>
<summary><strong>🔢 Математика (5)</strong></summary>

- **is_prime** — проверка числа на простоту
- **gcd** — наибольший общий делитель
- **lcm** — наименьшее общее кратное
- **factorial** — факториал числа
- **fibonacci** — n-е число Фибоначчи
</details>

<details>
<summary><strong>📐 Линейная алгебра (8)</strong></summary>

- **vector_add** / **vector_subtract** — покомпонентные операции над векторами
- **vector_dot** — скалярное произведение векторов
- **vector_norm** — норма (длина) вектора
- **matrix_multiply** — произведение матриц
- **matrix_transpose** — транспонирование матрицы
- **matrix_determinant** — определитель квадратной матрицы
- **matrix_inverse** — обратная матрица
- 🧮 На базе NumPy
</details>

<details>
<summary><strong>✅ Валидация текста (5)</strong></summary>

- **validate_email** / **validate_url** — проверка формата email и URL
- **extract_emails** / **extract_urls** — извлечение email/URL из текста
- **slugify** — преобразование текста в URL-safe slug
</details>

<details>
<summary><strong>🖼 Изображения (7)</strong></summary>

- **get_image_info** — размеры, формат, режим цвета, размер файла
- **resize_image** — изменение размера изображения
- **crop_image** — обрезка по координатам
- **rotate_image** — поворот на заданный угол
- **convert_format** — конвертация формата (по расширению выходного файла)
- **create_thumbnail** — миниатюра с сохранением пропорций
- **add_watermark** — текстовый водяной знак
- 🎨 На базе Pillow
</details>

<details>
<summary><strong>📈 Графики (10)</strong></summary>

- **plot_line** / **plot_scatter** / **plot_area** — линейный график, диаграмма рассеяния, график с заливкой
- **plot_bar** / **plot_stacked_bar** — столбчатая и накопительная столбчатая диаграммы
- **plot_pie** — круговая диаграмма
- **plot_histogram** — гистограмма
- **plot_boxplot** — box plot для одного или нескольких наборов данных
- **plot_multi_line** — несколько линий на одном графике
- **plot_from_csv** — построение графика прямо из CSV-файла рабочей директории
- 📊 На базе Matplotlib
</details>

<details>
<summary><strong>🔲 QR-коды (10)</strong></summary>

- **generate_qr_code** — базовый QR-код из текста или ссылки
- **generate_qr_code_colored** — QR-код с настраиваемыми цветами
- **generate_qr_with_logo** — QR-код с логотипом по центру
- **generate_wifi_qr** — QR-код для подключения к Wi-Fi
- **generate_vcard_qr** — QR-код визитки (vCard)
- **generate_sms_qr** — QR-код для отправки SMS
- **generate_email_qr** — QR-код для письма (mailto)
- **generate_geo_qr** — QR-код геолокации
- **batch_generate_qr** — пакетная генерация нескольких QR-кодов
- **read_qr_code** — распознавание и декодирование QR-кода с изображения
- 📷 Генерация на qrcode, распознавание на OpenCV (без системных зависимостей)
</details>

<details>
<summary><strong>📊 Штрихкоды (4)</strong></summary>

- **generate_barcode** — линейный штрихкод (Code128, EAN13, EAN8, UPC, Code39, ISBN и др.)
- **list_barcode_types** — список поддерживаемых типов штрихкодов
- **batch_generate_barcode** — пакетная генерация нескольких штрихкодов
- **read_barcode** — распознавание и декодирование штрихкода с изображения
- 🏷 Генерация на python-barcode, распознавание на pyzbar (требует системную библиотеку libzbar)
</details>

---

## 📸 Демонстрация

![](screenshots/01-help.png)

![](screenshots/02-tools.png)

![](screenshots/03-list-directory.png)

![](screenshots/04-read-file.png)

![](screenshots/05-search-files.png)

![](screenshots/06-create-file.png)

![](screenshots/07-security.png)
---

## 🚀 Быстрый старт

### Требования
- Python 3.12+
- Yandex Cloud API ключ (для LLM)
- GitHub Personal Access Token
- Google OAuth Access Token (для Google Sheets)
- Системная библиотека `libzbar0` (для чтения штрихкодов, `read_barcode`) — на Debian/Ubuntu: `apt-get install libzbar0`

### Установка
```bash
git clone https://github.com/Artem-Kornilov-pro/mcp-ai-assistant.git
cd mcp-ai-assistant
make install
```

### Настройка
```bash
cp .env.example .env
# Заполни .env своими ключами
```

### Запуск
```bash
make run
```

---

## 🏗 Архитектура проекта

```
mcp-ai-assistant/
├── src/
│   ├── __init__.py          # Пакет
│   ├── config.py            # Загрузка конфигурации из .env
│   ├── llm.py               # LLM-клиент (Yandex Cloud / DeepSeek)
│   ├── mcp_manager.py       # Менеджер MCP-инструментов
│   └── main.py              # Терминальный чат-интерфейс
├── servers/
│   ├── __init__.py
│   ├── filesystem.py        # Файловая система (4)
│   ├── github.py            # GitHub API (17)
│   ├── google_sheets.py     # Google Sheets (3)
│   ├── weather.py           # Погода wttr.in (8)
│   ├── datetime_tools.py    # Дата и время (8)
│   ├── sqlite_server.py     # Локальная SQLite БД (3)
│   ├── excel_server.py      # Excel (4)
│   ├── csv_server.py        # CSV (3)
│   ├── pdf_server.py        # PDF (3)
│   ├── archive_server.py    # ZIP-архивы (3)
│   ├── text_server.py       # Текстовые утилиты (5)
│   ├── random_server.py     # Случайные числа (5)
│   ├── math_server.py       # Математика (5)
│   ├── linalg_server.py     # Линейная алгебра (8)
│   ├── validate_server.py   # Валидация текста (5)
│   ├── image_server.py      # Изображения (7)
│   ├── chart_server.py      # Графики (10)
│   ├── qr_server.py         # QR-коды (10)
│   └── barcode_server.py    # Штрихкоды (4)
├── tests/
│   └── unit/                # По одному файлу тестов на каждый модуль выше
├── screenshots/             # Скриншоты работы
├── .github/workflows/
│   └── ci.yml               # CI/CD: ruff + pytest + mypy
├── workspace/               # Рабочая директория (файлы, БД)
├── pyproject.toml
├── Makefile
├── LICENSE
├── README.md
└── README.en.md
```

---

## 🧪 Тестирование и качество кода

```bash
make test        # pytest с покрытием (245+ тестов)
make lint        # ruff check + format check
make type-check  # mypy strict mode
```

**CI/CD**: GitHub Actions автоматически проверяет каждый PR и push в master:
- ✅ Ruff — линтер
- ✅ Pytest — юнит-тесты с coverage
- ✅ Mypy — строгая типизация

---

## 🔧 Технологический стек

| Категория | Технология |
|-----------|-----------|
| Язык | Python 3.12 |
| LLM | Yandex Cloud / DeepSeek (OpenAI-совместимый API) |
| MCP | FastMCP |
| HTTP | httpx (асинхронный) |
| Конфигурация | python-dotenv, Pydantic |
| Линейная алгебра | NumPy |
| Изображения | Pillow |
| Графики | Matplotlib |
| QR-коды | qrcode, OpenCV |
| Штрихкоды | python-barcode, pyzbar |
| Тестирование | pytest, pytest-cov, pytest-asyncio |
| Линтер | ruff |
| Типизация | mypy (strict mode) |
| CI/CD | GitHub Actions |

---

## 📋 Примеры запросов

```text
# Файлы
"покажи содержимое корневой папки workspace"
"найди все Python файлы в src/"
"создай файл notes.md с текстом ..."

# GitHub
"покажи список моих репозиториев на GitHub"
"создай issue в user/repo с заголовком 'Баг'"
"создай PR из ветки feature в main"

# Google Sheets
"создай таблицу 'Мои заметки'"
"запиши в <ID> в ячейку A1 значение 'Привет'"
"прочитай таблицу <ID>"
```

---

## 🔮 Планы развития

- [ ] MCP-сервер для Telegram (отправка сообщений)
- [ ] MCP-сервер для работы с браузером (Playwright)
- [ ] Веб-интерфейс (FastAPI + WebSocket)
- [ ] Поддержка нескольких LLM-провайдеров (Ollama, Anthropic)
- [ ] RAG (Retrieval-Augmented Generation) для работы с документами
- [ ] Агентные цепочки (Agent Chains) для сложных сценариев

---

## 📄 Лицензия

MIT — используйте, модифицируйте, распространяйте.

---

## 👤 Автор

**Artem Kornilov** — [GitHub](https://github.com/Artem-Kornilov-pro)
