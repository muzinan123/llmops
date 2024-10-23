#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
from uuid import UUID

from celery import shared_task
from flask import current_app


@shared_task
def demo_task(id: UUID) -> str:
    time.sleep(5)
    logging.info(f"id:{id}")
    logging.info(f"xxxx:{current_app.config}")
    return "xxxx"
