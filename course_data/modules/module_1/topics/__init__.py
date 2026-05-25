# -*- coding: utf-8 -*-
"""Опубликованные темы 6–11 модуля 1."""

from __future__ import annotations

from course_data.modules.module_1.topics.topic_06 import TOPIC as TOPIC_06
from course_data.modules.module_1.topics.topic_07 import TOPIC as TOPIC_07
from course_data.modules.module_1.topics.topic_08 import TOPIC as TOPIC_08
from course_data.modules.module_1.topics.topic_09 import TOPIC as TOPIC_09
from course_data.modules.module_1.topics.topic_10 import TOPIC as TOPIC_10
from course_data.modules.module_1.topics.topic_11 import TOPIC as TOPIC_11

_PUBLISHED_6_11 = (
    TOPIC_06,
    TOPIC_07,
    TOPIC_08,
    TOPIC_09,
    TOPIC_10,
    TOPIC_11,
)


def get_topics_6_11() -> list[dict]:
    return list(_PUBLISHED_6_11)
