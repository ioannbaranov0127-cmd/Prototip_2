# -*- coding: utf-8 -*-
"""Темы модуля 2."""

from __future__ import annotations

from course_data.modules.module_2.topics.topic_01 import TOPIC as TOPIC_01
from course_data.modules.module_2.topics.topic_02 import TOPIC as TOPIC_02
from course_data.modules.module_2.topics.topic_03 import TOPIC as TOPIC_03

_ALL = (TOPIC_01, TOPIC_02, TOPIC_03)


def get_topics() -> list[dict]:
    return list(_ALL)
