# Инструкция по генерации PDF из отчета

## Способ 1: Использование Pandoc (рекомендуется)

### Установка Pandoc

**Windows:**
```powershell
# Через Chocolatey
choco install pandoc

# Или скачать с https://pandoc.org/installing.html
```

**Linux:**
```bash
sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended
```

**macOS:**
```bash
brew install pandoc
brew install --cask basictex
```

### Генерация PDF

```bash
pandoc report.md -o report.pdf --pdf-engine=xelatex -V geometry:margin=2cm
```

Или с более продвинутыми настройками:

```bash
pandoc report.md -o report.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=2cm \
  -V fontsize=12pt \
  -V documentclass=article \
  --toc
```

## Способ 2: Использование онлайн-конвертеров

1. **Markdown to PDF:**
   - https://www.markdowntopdf.com/
   - Загрузите файл `report.md` и скачайте PDF

2. **Dillinger:**
   - https://dillinger.io/
   - Откройте файл, нажмите "Export as" → "PDF"

3. **StackEdit:**
   - https://stackedit.io/
   - Импортируйте файл, экспортируйте как PDF

## Способ 3: Использование VS Code

1. Установите расширение "Markdown PDF"
2. Откройте `report.md`
3. Нажмите `Ctrl+Shift+P` (или `Cmd+Shift+P` на Mac)
4. Выберите "Markdown PDF: Export (pdf)"

## Способ 4: Использование Google Docs / Microsoft Word

1. Откройте `report.md` в текстовом редакторе
2. Скопируйте содержимое
3. Вставьте в Google Docs или Microsoft Word
4. Отформатируйте при необходимости
5. Экспортируйте как PDF

## Примечания

- Для корректного отображения PlantUML кода в PDF может потребоваться дополнительная настройка
- Скриншоты диаграмм необходимо добавить вручную после генерации изображений из PlantUML
- Убедитесь, что в отчете заполнено поле "Ф.И.О. студента" (Джафари Хоссаин)

