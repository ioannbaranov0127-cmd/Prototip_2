# -*- coding: utf-8 -*-
"""Модуль 2: списки и развитие проекта."""

from __future__ import annotations

from course_data.modules.module_2.topics import get_topics
from course_data.registry import finalize_topic


def get_all_topics() -> list[dict]:
    return [finalize_topic(t) for t in get_topics()]
