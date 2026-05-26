# -*- coding: utf-8 -*-
"""Шаги проекта для тем модуля 2."""

from __future__ import annotations

from course_data.project import PROJECT_NAME

MODULE_2_PROJECT: dict[int, dict] = {
    1: {
        'goal': 'Повторить и освежить ключевые части калькулятора калорий.',
        'milestone': 'Ввод продукта, расчёт, условия и циклы — без новых конструкций.',
    },
    2: {
        'goal': 'Хранить названия продуктов и калорийность в списках.',
        'milestone': 'Два списка: продукты и kcal на 100 г, доступ по индексу.',
    },
    3: {
        'goal': 'Вести список введённых продуктов и считать их количество.',
        'milestone': 'append(), remove() и len() в логике калькулятора.',
    },
}


def project_step_for_module_2(num: int) -> dict:
    row = MODULE_2_PROJECT.get(num, {})
    return {
        'project': PROJECT_NAME,
        'goal': row.get('goal', ''),
        'milestone': row.get('milestone', ''),
    }
