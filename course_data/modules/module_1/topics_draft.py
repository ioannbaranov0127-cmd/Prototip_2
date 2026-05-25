# -*- coding: utf-8 -*-
"""
Черновые темы 12–17: структура и project_step готовы, задания — заготовки.
Подключаются в модуль 1, когда INCLUDE_DRAFT_TOPICS = True в constants.py.
"""

from __future__ import annotations

from course_data.project import PROJECT_NAME, project_step_for_topic

# (num, slug, short_title, summary)
_DRAFT_META: list[tuple[int, str, str, str]] = [
    (12, 'while', 'Цикл while', 'Главный цикл программы.'),
    (13, 'integrate', 'Интеграция проекта', 'Сборка ядра калькулятора.'),
    (14, 'extend', 'Индивидуальные доработки', 'Новые продукты и улучшения.'),
    (15, 'final_build', 'Финальная сборка', 'Полная версия проекта.'),
    (16, 'errors', 'Обработка ошибок', 'Корректная работа при неверном вводе.'),
    (17, 'defense', 'Защита проекта', 'Демонстрация и объяснение алгоритма.'),
]


def _stub_theory(summary: str, goal: str) -> dict:
    return {
        'intro': summary,
        'sections': [
            {
                'title': 'Шаг проекта «Калькулятор калорий»',
                'body': goal,
            },
        ],
        'visual_blocks': [],
        'schemes': [],
        'remember': ['Каждая тема добавляет новую часть в общий проект.'],
        'mistakes': [],
        'tips': ['Вернитесь к предыдущим темам, если нужно освежить базовые команды.'],
    }


def _stub_task(task_id: int, num: int, goal: str) -> dict:
    return {
        'id': task_id,
        'kind': 'theory',
        'type': 'quiz',
        'category': 'theory',
        'text': (
            f'Тема {num} в подготовке. Какой шаг проекта «{PROJECT_NAME}» '
            f'мы будем делать на этом этапе?'
        ),
        'hint': goal,
        'xp': 5,
        'options': [
            {'key': 'a', 'label': 'Шаг из описания темы (см. теорию)'},
            {'key': 'b', 'label': 'Сразу писать полный калькулятор без шагов'},
            {'key': 'c', 'label': 'Удалить все переменные из проекта'},
        ],
        'correct': 'a',
        'draft': True,
    }


def get_draft_topics() -> list[dict]:
    topics: list[dict] = []
    task_id = 60
    for num, slug, short_title, summary in _DRAFT_META:
        step = project_step_for_topic(num)
        topics.append({
            'id': f'm1-t{num}',
            'num': num,
            'title': f'Тема {num}. {short_title}',
            'summary': summary,
            'draft': True,
            'project_step': step,
            'theory': _stub_theory(summary, step['goal']),
            'tasks': [_stub_task(task_id, num, step['goal'])],
        })
        task_id += 1
    return topics