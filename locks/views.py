"""
locks/views.py
Oracle Lock Monitor - Django Views & API
"""

import json
import logging
from datetime import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from . import oracle_client as oc

logger = logging.getLogger(__name__)


# ── Helper ───────────────────────────────────────

def _ok(data=None, **kwargs):
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    payload.update(kwargs)
    return JsonResponse(payload)


def _err(msg, status=400):
    return JsonResponse({"success": False, "error": str(msg)}, status=status)


def _session_key(request):
    """使用 Django session key 識別使用者的連線"""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


# ── 主頁面 ───────────────────────────────────────

def index(request):
    demo = oc.is_demo_mode()
    connected = oc.is_connected(_session_key(request))
    return render(request, 'locks/index.html', {
        'demo_mode': demo,
        'connected': connected,
        'default_host': settings.DEFAULT_DB_HOST,
    })


# ── API: 連線管理 ────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def api_connect(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return _err("無效的 JSON")

    host    = body.get("host", "").strip()
    port    = body.get("port", "1521").strip()
    service = body.get("service", "").strip()
    user    = body.get("user", "").strip()
    password = body.get("password", "")

    if not all([host, port, service, user, password]):
        return _err("請填寫所有連線欄位")

    try:
        oc.connect(_session_key(request), host, port, service, user, password)
        return _ok(message="連線成功")
    except Exception as e:
        logger.error("Connect failed: %s", e)
        return _err(f"連線失敗: {e}", status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_disconnect(request):
    oc.disconnect(_session_key(request))
    return _ok(message="已斷線")


# ── API: 取得 Lock 資料 ──────────────────────────

@require_http_methods(["GET"])
def api_locks(request):
    try:
        rows = oc.fetch_locks(_session_key(request))
        return _ok(
            rows=rows,
            count=len(rows),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            demo=oc.is_demo_mode(),
            connected=oc.is_connected(_session_key(request)),
        )
    except Exception as e:
        logger.error("Fetch locks failed: %s", e)
        return _err(str(e), status=500)


# ── API: Kill Session ────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def api_kill_session(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return _err("無效的 JSON")

    sid    = body.get("sid", "").strip()
    serial = body.get("serial", "").strip()

    if not sid or not serial:
        return _err("缺少 sid 或 serial")

    try:
        oc.kill_session(_session_key(request), sid, serial)
        msg = f"[Demo] Kill Session SID={sid},SERIAL#={serial} 指令已送出" \
              if oc.is_demo_mode() else \
              f"Kill Session SID={sid},SERIAL#={serial} 執行成功"
        return _ok(message=msg)
    except Exception as e:
        logger.error("Kill session failed: %s", e)
        return _err(str(e), status=500)


# ── API: Kill OS Process ─────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def api_kill_process(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return _err("無效的 JSON")

    pid = body.get("pid", "").strip()
    if not pid:
        return _err("缺少 pid")

    try:
        oc.kill_os_process(pid)
        return _ok(message=f"Kill Process PID={pid} 執行成功")
    except Exception as e:
        logger.error("Kill process failed: %s", e)
        return _err(str(e), status=500)
