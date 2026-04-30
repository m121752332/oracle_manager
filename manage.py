#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oracle_monitor.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django 未安裝，請執行: pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)
