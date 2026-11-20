# Лабораторная 2.0 – подготовка тестовых данных для GitHub

## Назначение

Комплект наполняет ранее созданный `parts-unlimited-labs` файлами демонстрационного веб-приложения и тестовыми GitHub Issues, Labels, Milestones. Не содержит workflows GitHub Actions, не создает Teams и не изменяет настройки GitHub Projects: эти операции предусмотрены следующими работами.

## Содержимое

- `docs/index.html`, `docs/styles.css`, `docs/catalog.mjs`, `docs/site.mjs` – статический демонстрационный каталог, пригодный для будущего GitHub Pages.
- `tests/catalog.test.mjs` – автоматические тесты бизнес-логики.
- `package.json` – команда `npm test` (внешние пакеты не нужны).
- `fixtures/issues.json` – 24 синтетических рабочих элемента с эпиками, функциями, историями, задачами и дефектами.
- `scripts/seed_github.py` – идемпотентная загрузка Issues, Labels, Milestones и опциональное добавление Issues в GitHub Project.

## Предварительные условия

- Существующий публичный репозиторий `ORGANIZATION/parts-unlimited-labs` из лабораторной 1.1.
- Git.
- Python 3.9 или новее.
- Node.js 20 или новее.
- GitHub CLI (gh), прошедший авторизацию `gh auth login` (нужны права на репозиторий). Для Project может понадобиться `gh auth refresh -s project`.

## Добавление исходных файлов

1. Клонируйте основной репозиторий:

   ```bash
   git clone https://github.com/ORGANIZATION/parts-unlimited-labs.git
   cd parts-unlimited-labs
   ```

2. Распакуйте папки `docs`, `tests`, `fixtures`, `scripts` и файлы `package.json`, `LAB-2.0.md` из этого комплекта в корень клонированного репозитория. Не заменяйте существующий `README.md` и не удаляйте Wiki.

3. Проверьте тесты:

   ```bash
   npm test
   ```

4. Просмотрите план загрузки данных (без изменений GitHub):

   ```bash
   python scripts/seed_github.py --repo ORGANIZATION/parts-unlimited-labs
   ```

5. Выполните загрузку:

   ```bash
   gh auth login
   python scripts/seed_github.py --repo ORGANIZATION/parts-unlimited-labs --apply
   ```

6. Если известен номер существующего GitHub Project (например, `.../projects/2`), можно сразу добавить Issues в него:

   ```bash
   gh auth refresh -s project
   python scripts/seed_github.py --repo ORGANIZATION/parts-unlimited-labs --project-number 2 --apply
   ```

7. Опубликуйте локальные исходники:

   ```bash
   git add docs tests fixtures scripts package.json LAB-2.0.md
   git commit -m "Подготовлены тестовые данные лабораторной 2.0"
   git push origin main
   ```

## Проверка

- `npm test` завершается успешно.
- `python -m http.server 8000 --directory docs` и адрес `http://localhost:8000` открывают каталог товаров.
- В Issues видны 24 учебные задачи, из них 5 закрытых, все с меткой `seed:lab2.0`.
- Есть 13 меток (могут существовать и дополнительные стандартные метки).
- Есть 3 milestones, Sprint 1 с прошедшей датой, Sprint 2 текущий, Sprint 3 следующий.
- При повторном запуске скрипт не создает дублированных Issues с маркером `parts-unlimited-seed:v1`.
- При `--project-number` все 24 Issues появляются в проекте.

## Ограничения

Это учебный аналог шаблона Parts Unlimited, а не копия оригинальной базы данных, репозиториев, конвейеров и инфраструктуры Azure DevOps. Закрытые Issues создаются сегодня и закрываются сегодня; историческое время создания GitHub не подделывается. Специализированные поля и представления Scrum/Kanban добавляются в следующих работах. Первая загрузка делает реальные запросы в GitHub только после явного `--apply`.
