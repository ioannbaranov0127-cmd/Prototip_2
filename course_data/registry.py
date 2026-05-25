# -*- coding: utf-8 -*-
"""Нормализация тем и заданий перед сборкой LESSONS."""

from __future__ import annotations

from course_data.task_types import normalize_task


def finalize_topic(topic: dict) -> dict:
    """Копия темы с нормализованными заданиями и полями num / project_step."""
    row = dict(topic)
    tasks = row.get('tasks') or []
    row['tasks'] = [normalize_task(t) for t in tasks]
    return row


def flatten_module_tasks(module: dict) -> list[dict]:
    out: list[dict] = []
    for topic in module.get('topics') or []:
        tid = topic['id']
        ttitle = topic['title']
        tnum = topic.get('num')
        for task in topic.get('tasks') or []:
            row = {**task, 'topic_id': tid, 'topic_title': ttitle}
            if tnum is not None:
                row['topic_num'] = tnum
            if 'type' not in row:
                row['type'] = 'code'
            out.append(row)
    return out
