"""
oracle_client.py
Oracle 連線管理模組
- Thread-safe session 級別連線快取
- Demo 模式（oracledb 未安裝時）
"""

import os
import signal
import logging
import threading

logger = logging.getLogger(__name__)

# ── oracledb 可選 ──────────────────────────────
try:
    import oracledb
    
    # 為了支援 Oracle 11g，必須啟用 Thick mode (厚客戶端模式)。
    # 系統必須安裝 Oracle Instant Client (Windows: 請加入 PATH，或指定 lib_dir)
    try:
        oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_11_2_64")
        logger.info("已啟用 oracledb Thick mode (支援 Oracle 11g)")
    except Exception as e:
        logger.warning("無法啟用 oracledb Thick mode，若不需要連線 11g 可忽略。錯誤: %s", e)

    ORACLEDB_AVAILABLE = True
except ImportError:
    ORACLEDB_AVAILABLE = False
    logger.warning("oracledb 未安裝，系統將以 Demo 模式運行")

# ── 全域連線池（key = session_key） ─────────────
_connections = {}
_conn_lock   = threading.Lock()

# ── Demo 假資料 ──────────────────────────────────
DEMO_ROWS = [
    {
        "sid": "42",       "serial": "1234",  "process": "9981",
        "username": "APPUSER",  "osuser": "oracle", "machine": "app-srv-01",
        "program": "JDBC Thin Client",
        "object_name": "ORDERS", "object_type": "TABLE",
        "lock_type": "TM", "lock_mode": "Row-X (6)",
        "request": "None",  "block": "1 (Blocker)",
        "status": "ACTIVE", "logon_time": "2024-04-28 09:12:00",
        "ctime": "3600"
    },
    {
        "sid": "87",       "serial": "5678",  "process": "2231",
        "username": "SYSUSER", "osuser": "appusr", "machine": "web-srv-02",
        "program": "sqlplus@web-srv-02",
        "object_name": "USERS", "object_type": "TABLE",
        "lock_type": "TX", "lock_mode": "Exclusive (6)",
        "request": "None",  "block": "0",
        "status": "ACTIVE", "logon_time": "2024-04-28 10:05:33",
        "ctime": "120"
    },
    {
        "sid": "103",      "serial": "9012",  "process": "4412",
        "username": "BATCH", "osuser": "batch", "machine": "batch-srv-01",
        "program": "Python3 batch_job.py",
        "object_name": "INVENTORY", "object_type": "TABLE",
        "lock_type": "TM", "lock_mode": "Row-S (2)",
        "request": "Share (4)", "block": "0",
        "status": "INACTIVE", "logon_time": "2024-04-28 08:30:11",
        "ctime": "45"
    },
    {
        "sid": "215",      "serial": "3301",  "process": "7762",
        "username": "REPUSER", "osuser": "repusr", "machine": "rpt-srv-03",
        "program": "Report Generator",
        "object_name": "SALES_SUMMARY", "object_type": "TABLE",
        "lock_type": "TM", "lock_mode": "Row-X (6)",
        "request": "None",  "block": "0",
        "status": "ACTIVE", "logon_time": "2024-04-28 11:20:45",
        "ctime": "900"
    },
]

# ── SQL ─────────────────────────────────────────
LOCK_SQL = """
SELECT
    s.sid,
    s.serial#                           AS serial_num,
    p.spid                              AS process,
    s.process                           AS os_process,
    NVL(s.username, '(SYS)')           AS username,
    NVL(s.osuser,  '-')                AS osuser,
    NVL(s.machine, '-')                AS machine,
    NVL(s.program, '-')                AS program,
    NVL(o.object_name, '(TX lock)')    AS object_name,
    NVL(o.object_type, '-')            AS object_type,
    l.type                              AS lock_type,
    DECODE(l.lmode,
        0,'None (0)',   1,'Null (1)',   2,'Row-S (2)',
        3,'Row-X (3)',  4,'Share (4)',  5,'S/Row-X (5)',
        6,'Exclusive (6)', TO_CHAR(l.lmode)) AS lock_mode,
    DECODE(l.request,
        0,'None',       1,'Null',      2,'Row-S',
        3,'Row-X',      4,'Share',     5,'S/Row-X',
        6,'Exclusive',  TO_CHAR(l.request)) AS request,
    DECODE(l.block, 0,'0', 1,'1 (Blocker)', TO_CHAR(l.block)) AS block_flag,
    s.status,
    TO_CHAR(s.logon_time,'YYYY-MM-DD HH24:MI:SS') AS logon_time,
    l.ctime                             AS ctime
FROM v$lock l
JOIN v$session s ON l.sid = s.sid
LEFT JOIN dba_objects o ON l.id1 = o.object_id
LEFT JOIN v$process p ON s.paddr = p.addr
WHERE l.type IN ('TM','TX')
  AND s.type != 'BACKGROUND'
ORDER BY l.block DESC, s.sid
"""


# ────────────────────────────────────────────────
# 對外介面
# ────────────────────────────────────────────────

def is_demo_mode():
    return not ORACLEDB_AVAILABLE


def connect(session_key, host, port, service, user, password):
    """
    建立 Oracle 連線並存入快取。
    成功回傳 None，失敗拋出 Exception。
    """
    if not ORACLEDB_AVAILABLE:
        raise RuntimeError("oracledb 未安裝，無法連線真實 Oracle")

    dsn  = oracledb.makedsn(host, int(port), service_name=service)
    conn = oracledb.connect(user=user, password=password, dsn=dsn)
    with _conn_lock:
        _close_session(session_key)      # 先關舊的
        _connections[session_key] = conn
    logger.info("Session %s 已連線 Oracle %s/%s", session_key, host, service)


def disconnect(session_key):
    with _conn_lock:
        _close_session(session_key)
    logger.info("Session %s 已斷線", session_key)


def is_connected(session_key):
    with _conn_lock:
        return session_key in _connections


def fetch_locks(session_key):
    """
    查詢鎖定資料，回傳 list[dict]。
    Demo 模式直接回傳假資料。
    """
    if not ORACLEDB_AVAILABLE:
        return list(DEMO_ROWS)

    with _conn_lock:
        conn = _connections.get(session_key)
    if conn is None:
        raise RuntimeError("尚未連線，請先 Connect")

    try:
        cursor = conn.cursor()
        cursor.execute(LOCK_SQL)
        cols = [d[0].lower() for d in cursor.description]
        # 將 serial_num → serial，block_flag → block
        key_map = {"serial_num": "serial", "block_flag": "block"}
        rows = []
        for raw in cursor.fetchall():
            row = {}
            for k, v in zip(cols, raw):
                real_key = key_map.get(k, k)
                row[real_key] = str(v) if v is not None else ""
            rows.append(row)
        cursor.close()
        return rows
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        # ORA-03113/03114 表示連線中斷
        if error_obj.code in (3113, 3114, 1012):
            with _conn_lock:
                _close_session(session_key)
        raise


def kill_session(session_key, sid, serial):
    """執行 ALTER SYSTEM KILL SESSION"""
    if not ORACLEDB_AVAILABLE:
        logger.info("[Demo] Kill Session SID=%s SERIAL#=%s", sid, serial)
        return

    with _conn_lock:
        conn = _connections.get(session_key)
    if conn is None:
        raise RuntimeError("尚未連線")

    sql = f"ALTER SYSTEM KILL SESSION '{sid},{serial}' IMMEDIATE"
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        cursor.close()
        logger.info("Kill Session 成功: SID=%s SERIAL#=%s", sid, serial)
    except oracledb.DatabaseError as e:
        logger.error("Kill Session 失敗: %s", e)
        raise


def kill_os_process(pid_str):
    """對 OS Process 發送 SIGKILL"""
    try:
        pid = int(pid_str)
    except (ValueError, TypeError):
        raise ValueError(f"無效的 PID: {pid_str!r}")

    try:
        os.kill(pid, signal.SIGKILL)
        logger.info("Kill OS PID=%s 成功", pid)
    except ProcessLookupError:
        raise RuntimeError(f"Process {pid} 不存在")
    except PermissionError:
        raise RuntimeError(f"無權限 Kill Process {pid}（需 root 或同 UID）")


# ── 內部工具 ─────────────────────────────────────
def _close_session(session_key):
    conn = _connections.pop(session_key, None)
    if conn:
        try:
            conn.close()
        except Exception:
            pass
