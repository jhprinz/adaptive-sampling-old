#!/usr/bin/env bash

# needs to be executed where task.py is

celery worker -A tasks -l INFO --concurrency=4