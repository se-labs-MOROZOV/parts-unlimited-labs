#!/usr/bin/env python3
"""Идемпотентная загрузка учебных Issues, Labels и Milestones в GitHub.

Требования: Python 3.9+, GitHub CLI (gh) и авторизация через gh auth login.
Без --apply только показывает план, без доступа к GitHub и изменений.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "fixtures" / "issues.json"
MARKER_PREFIX = "parts-unlimited-seed:v1:"
LABELS = {
    "seed:lab2.0": ("45639a", "Демонстрационные данные лабораторной 2.0"),
    "type:epic": ("6f42c1", "Эпик"),
    "type:feature": ("8250df", "Функциональность"),
    "type:story": ("1f6feb", "История пользователя"),
    "type:task": ("2da44e", "Задача"),
    "type:bug": ("d73a49", "Ошибка"),
    "area:web": ("0e8a16", "Веб-приложение"),
    "area:qa": ("e6a700", "Тестирование"),
    "area:platform": ("5319e7", "Инфраструктура и поставка"),
    "area:data": ("1d76db", "Данные каталога"),
    "priority:p1": ("b60205", "Высокий приоритет"),
    "priority:p2": ("fbca04", "Средний приоритет"),
    "priority:p3": ("c5def5", "Низкий приоритет"),
}


def run(*args: str, input_data: str | None = None) -> str:
    command = list(args)
    completed = subprocess.run(command, input=input_data, text=True, capture_output=True, encoding="utf-8")
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"Ошибка команды {command[0]}: {message}")
    return completed.stdout.strip()


def body_for(issue: dict, urls: dict[str, str]) -> str:
    parent = issue.get("parent")
    parent_line = f"**Родительский элемент:** {urls[parent]}\n\n" if parent and parent in urls else ""
    state_note = "выполнена (тестовая история)" if issue["state"] == "closed" else "ожидает работы (тестовая история)"
    return (
        f"<!-- {MARKER_PREFIX}{issue['id']} -->\n"
        f"## Описание\n\n{issue['description']}\n\n"
        f"{parent_line}"
        f"**Область:** {issue['area']}  \n"
        f"**Приоритет:** {issue['priority'].upper()}  \n"
        f"**Оценка:** {issue.get('points') or 'не указана'} SP  \n"
        f"**Состояние тестового сценария:** {state_note}\n\n"
        "## Критерии приемки\n\n"
        f"- [{'x' if issue['state'] == 'closed' else ' '}] Сценарий проверен по описанию.\n\n"
        "_Синтетические учебные данные, не реальные пользовательские обращения._\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="OWNER/REPO, например se-labs-user/parts-unlimited-labs")
    parser.add_argument("--apply", action="store_true", help="Действительно создать объекты в GitHub")
    parser.add_argument("--project-number", type=int, default=None, help="При необходимости добавить Issues в GitHub Project указанного номера")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+", args.repo):
        parser.error("--repo должен иметь вид OWNER/REPO")
    if args.project_number is not None and args.project_number < 1:
        parser.error("Номер проекта должен быть положительным")

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    unique = {item["id"] for item in data}
    if len(unique) != len(data):
        raise RuntimeError("В fixtures/issues.json есть повторяющиеся ID")
    if any(item.get("parent") not in unique for item in data if item.get("parent")):
        raise RuntimeError("В fixtures/issues.json есть ссылка на отсутствующий родительский элемент")

    owner, _ = args.repo.split("/", 1)
    print(f"Цель: {args.repo}")
    print(f"План: {len(LABELS)} меток, 3 milestones, {len(data)} Issues (из них "
          f"{sum(i['state'] == 'closed' for i in data)} закрытых).")
    if args.project_number:
        print(f"Дополнительно: GitHub Project №{args.project_number} организации {owner}.")
    if not args.apply:
        print("Предпросмотр: GitHub не изменен. Для загрузки добавьте --apply.")
        return 0

    if shutil.which("gh") is None:
        raise RuntimeError("Не найдена команда gh. Установите GitHub CLI.")
    run("gh", "auth", "status")
    verified = run("gh", "repo", "view", args.repo, "--json", "nameWithOwner")
    if json.loads(verified)["nameWithOwner"].lower() != args.repo.lower():
        raise RuntimeError("Проверка репозитория не пройдена")

    existing_labels = {x["name"] for x in json.loads(run("gh", "label", "list", "-R", args.repo, "--limit", "200", "--json", "name"))}
    for name, (color, description) in LABELS.items():
        if name not in existing_labels:
            run("gh", "label", "create", name, "-R", args.repo, "--color", color, "--description", description)
            print(f"LABEL + {name}")
        else:
            print(f"LABEL = {name}")

    today = datetime.now(timezone.utc).date()
    sprint_windows = [
        ("Sprint 1", -20, -7, "Прошедший учебный спринт"),
        ("Sprint 2", -6, 7, "Текущий учебный спринт"),
        ("Sprint 3", 8, 21, "Следующий учебный спринт"),
    ]
    milestones = json.loads(run("gh", "api", f"repos/{args.repo}/milestones?state=all&per_page=100"))
    existing_milestones = {m["title"] for m in milestones}
    for title, start, end, description in sprint_windows:
        begin = today + timedelta(days=start)
        finish = today + timedelta(days=end)
        if title in existing_milestones:
            print(f"MILESTONE = {title} (существующий не изменен)")
            continue
        payload = {
            "title": title,
            "description": f"{description}. Интервал: {begin.isoformat()} – {finish.isoformat()} (UTC).",
            "due_on": finish.isoformat() + "T23:59:59Z",
        }
        run("gh", "api", "-X", "POST", f"repos/{args.repo}/milestones", "--input", "-", input_data=json.dumps(payload, ensure_ascii=True))
        print(f"MILESTONE + {title}")

    all_issues = json.loads(run("gh", "issue", "list", "-R", args.repo, "--state", "all", "--limit", "500", "--json", "number,body,url"))
    if len(all_issues) >= 500:
        raise RuntimeError("В репозитории >= 500 Issues. Уточните проверку дублей перед повторным запуском.")
    existing = {}
    for item in all_issues:
        match = re.search(r"<!--\s*" + re.escape(MARKER_PREFIX) + r"([A-Za-z0-9]+)\s*-->", item.get("body") or "")
        if match:
            existing[match.group(1)] = item["url"]
    urls = dict(existing)
    created = 0
    for item in data:
        ident = item["id"]
        if ident in existing:
            print(f"ISSUE = {ident}: {urls[ident]}")
            continue
        labels = ["seed:lab2.0", f"type:{item['kind']}", f"area:{item['area'].lower()}", f"priority:{item['priority']}"]
        params = ["gh", "issue", "create", "-R", args.repo, "--title", f"[{item['kind'].upper()}] {item['title']}", "--body", body_for(item, urls)]
        for label in labels:
            params.extend(["--label", label])
        if item.get("milestone"):
            params.extend(["--milestone", item["milestone"]])
        url = run(*params).splitlines()[-1].strip()
        if not re.fullmatch(r"https://github\.com/[^ ]+/issues/\d+", url):
            raise RuntimeError(f"Неожиданный URL созданной Issue: {url}")
        urls[ident] = url
        created += 1
        print(f"ISSUE + {ident}: {url}")
        if item["state"] == "closed":
            number = url.rsplit("/", 1)[-1]
            run("gh", "issue", "close", number, "-R", args.repo, "--reason", "completed")
            print(f"  CLOSED: {ident}")

    if args.project_number:
        for item in data:
            url = urls[item["id"]]
            run("gh", "project", "item-add", str(args.project_number), "--owner", owner, "--url", url)
            print(f"PROJECT + {item['id']}")
    print(f"Готово. Новых Issues: {created}, повторно использовано: {len(data) - created}.")
    print("Важно: дата создания закрытых Issues равна дате импорта, а не прошлому спринту.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ОШИБКА: {exc}", file=sys.stderr)
        print("После устранения ошибки повторите ту же команду: дубли не создаются по маркерам.", file=sys.stderr)
        sys.exit(1)
