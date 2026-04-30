# Oracle Manager

Python 3.7 + Django 2.2 LTS + uv
OS: Red Hat Enterprise Linux 6.6

---

## 功能

| 功能 | 說明 |
| ------ | ------ |
| 自動重抓 | 每 30 秒自動重新查詢 Lock 資料，倒數計時器即時顯示 |
| 手動重抓 | 點選「手動重抓」按鈕立即更新 |
| 欄位篩選 | 上方 Toggle 可隨時顯示/隱藏欄位，SID/PROCESS 為必要欄位 |
| 欄位排序 | 點選表頭可升降序排列 |
| Kill Lock | 執行 `ALTER SYSTEM KILL SESSION 'SID,SERIAL#' IMMEDIATE` |
| Kill PID | 執行 OS 層 `kill -9 PID` |
| Demo 模式 | oracledb 未安裝時自動切換假資料模式，UI 全功能可用 |

---

## 系統需求

- Python 3.7
- Red Hat Enterprise Linux 6.6
- Oracle Instant Client（連線真實 Oracle 時需要）
- oracledb 2.1.2

---

## 快速部署

```bash
# 1. 解壓後進入專案目錄
cd oracle_monitor

# 2. 執行部署腳本（自動建立 venv 並安裝套件）
bash deploy.sh

# 3. 啟動（開發）
.\venv\Scripts\Activate.ps1 #powershell
source venv/bin/activate
python manage.py runserver --bind 0.0.0.0:8000

# 4. 啟動（生產 gunicorn）
gunicorn oracle_monitor.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 60 \
  --daemon
```

---

## 安裝 oracledb（連線真實 Oracle）

```bash
# 1. 安裝 Oracle Instant Client RPM（依版本調整）
rpm -ivh oracle-instantclient19.8-basic-19.8.0.0.0-1.x86_64.rpm

# 2. 設定動態函式庫路徑
echo '/usr/lib/oracle/19.8/client64/lib' > /etc/ld.so.conf.d/oracle.conf
ldconfig

# 3. 安裝 oracledb
uv add oracledb
```

---

## API 端點

| Method | URL | 說明 |
| -------- | ---------- | ----------------------- |
| GET | `/` | 主介面 |
| POST | `/api/connect/` | 建立連線 `{host, port, service, user, password}` |
| POST | `/api/disconnect/` | 中斷連線 |
| GET | `/api/locks/` | 取得 Lock 資料（JSON） |
| POST | `/api/kill-session/` | Kill Session `{sid, serial}` |
| POST | `/api/kill-process/` | Kill Process `{pid}` |

---

## 必要 Oracle 權限

```sql
-- DBA 帳號連線，或授予以下權限：
GRANT SELECT ON v_$lock    TO monitor_user;
GRANT SELECT ON v_$session TO monitor_user;
GRANT SELECT ON v_$process TO monitor_user;
GRANT SELECT ON dba_objects TO monitor_user;
GRANT ALTER SYSTEM TO monitor_user;  -- Kill Session 用
```

---

## 專案結構

```plaintext
oracle_monitor/
├── manage.py
├── help.py                   ← 幫助make說明產生器
├── requirements.txt
├── deploy.sh
├── oracle_monitor/           ← Django 專案設定目錄
│   ├── settings.py           
│   ├── urls.py               
│   └── wsgi.py               
├── templates/                ← 全域樣版目錄
│   └── base.html             ← 共用的基礎版型 (套用 VS Code 風格的主佈局)
└── locks/                    ← Lock 監控 App
    ├── apps.py
    ├── oracle_client.py      ← oracledb 連線與 SQL 執行核心
    ├── urls.py               ← API 路由與網頁路由
    ├── views.py              ← API 邏輯與網頁渲染視圖
    └── templates/
        └── locks/
            └── index.html    ← Lock 監控單頁應用介面 (繼承 base.html)
```
