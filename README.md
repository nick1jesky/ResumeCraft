# 📄 ResumeCraft

**ResumeCraft** — это генератор профессиональных резюме, который форматирует в ваши вводные данные в красиво оформленные документы в форматах **HTML**, **PDF** и **DOCX** из **JSON** и **YAML** файлов.  

---

## ❓ Как пользоваться?

### Консоль

- `resumecraft [OPTIONS] [INPUT_FILE_NAME]`

### Опции [OPTIONS]

- `--help` - Список доступных команд.
- `--version` - Версия.
- `-o, --output PATH` - Директория вывода.
- `-f, --format [html|pdf|docx|all] [default: all]` - Выбор формата выходного документа. 
- `-t, --theme [clarity|modern|classic|minimal|executive|black-green] [default: clarity]` - Выбор темы.
- `-l, --lang [ru|en] [default: ru]` - Выбор языка.
- `--accent-color TEXT` - Цвет акцента в hex формате.
- `--font TEXT` - Шрифт.
- `--pdf-backend [weasyprint|pdfkit]` - backend PDF генерации.
- `--wkhtmltopdf-path PATH` - Путь к wkhtmltopdf (использовать только с --pdf-backend pdfkit)
- `--config PATH` - Путь к resumecraft.toml.
- `--debug` - Включить debug логирование.
- `--list-themes` - Список доступных тем.

## 📦 Требования

- **Python 3.10** или новее.
- Для генерации **PDF** дополнительно требуется один из бэкендов:
  - `weasyprint`
  - `pdfkit` + установленный [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)
