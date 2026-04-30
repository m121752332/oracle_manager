"""
Oracle Manager - Django Settings
Python 3.7 | Django 2.2 LTS | RHEL 6.6
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# 專案基礎路徑設定
# -----------------------------------------------------------------------------
# BASE_DIR 會指向專案的最外層根目錄 (例如 oracle_manager 資料夾)
# 作用：後續設定靜態檔案或模板路徑時，都是以此路徑作為基準
BASE_DIR = Path(__file__).resolve().parent.parent

# 載入 .env 檔案 (如果存在)
load_dotenv(os.path.join(BASE_DIR, '.env'))

# -----------------------------------------------------------------------------
# 核心安全設定
# -----------------------------------------------------------------------------
# SECRET_KEY 用於加密 Session、Cookie 以及密碼的雜湊運算。
# ⚠️ 警告：在正式生產環境中，這個值務必保密並透過環境變數注入，不可寫死在程式碼內！
SECRET_KEY = 'oracle-monitor-change-this-in-production-use-env-var'

# DEBUG 模式：開發時設為 True，如果發生錯誤會顯示詳細的錯誤追蹤頁面。
# ⚠️ 警告：正式環境務必改為 False，以免曝露系統設定檔或敏感資料。
DEBUG = True

# ALLOWED_HOSTS 指定允許哪些網域或 IP 可以存取這個 Django 網站。
# 當 DEBUG = False 時為必填。目前設為 '*' 代表允許所有，正式環境請限縮為實際 IP 或綁定網域。
ALLOWED_HOSTS = ['*']

# -----------------------------------------------------------------------------
# 應用程式與中介軟體設定
# -----------------------------------------------------------------------------
# INSTALLED_APPS 條列出這個 Django 專案啟用的所有應用模組。
INSTALLED_APPS = [
    'django.contrib.staticfiles', # 處理靜態檔案 (CSS, JS, 圖片等)
    'django.contrib.admin',       # 提供 Django 後台管理介面 (Admin Site)
    'django.contrib.auth',        # 提供用戶認證與授權系統 (User/Group/Permission)
    'django.contrib.sessions',    # 提供 Session 管理，讓 View 可以跨請求保存用戶資料
    'django.contrib.messages',    # 提供訊息框架，讓 View 可以傳遞一次性的訊息給模板顯示
    'django.contrib.contenttypes',# 提供內容類型系統，讓模型可以通用地關聯到其他模型 (如 GenericForeignKey)
    
    'locks',                      # 專案自定義的應用程式模組
]

# MIDDLEWARE 中介軟體會在 Request 抵達 View 之前、或 Response 離開 View 之後進行攔截與處理。
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # 提供多項基本的 HTTP 安全防護
    'django.contrib.sessions.middleware.SessionMiddleware',    # 管理用戶 Session 的中介軟體
    'django.middleware.common.CommonMiddleware',               # 處理基礎的 URL 重寫與封鎖（如加斜線）
    'django.middleware.csrf.CsrfViewMiddleware',               # 跨站請求偽造 (CSRF) 防護機制
    'django.contrib.auth.middleware.AuthenticationMiddleware', # 管理用戶認證狀態 (登入/登出)
    'django.contrib.messages.middleware.MessageMiddleware',    # 管理一次性訊息的中介軟體
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 點擊劫持防護 (防止被嵌入 iFrame)
]

# -----------------------------------------------------------------------------
# 路由與前端模板設定
# -----------------------------------------------------------------------------
# 指定專案 URL 路由的根入口設定檔（通常就是 urls.py）
ROOT_URLCONF = 'oracle_monitor.urls'

# TEMPLATES 定義 Django 如何尋找及渲染 HTML 模板。
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', # 使用 Django 內建的模板引擎
        'DIRS': [os.path.join(BASE_DIR, 'templates')],                # 將專案根目錄的 templates 資料夾加入搜尋路徑
        'APP_DIRS': True,                                             # 允許 Django 到各個 APP 內的 templates 資料夾中尋找
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',           # 在模板中提供 debug 相關的變數（如 debug 模式狀態）
                'django.template.context_processors.request',         # 在模板中提供 request 物件，讓模板可以存取當前請求的資訊
                'django.contrib.auth.context_processors.auth',        # 在模板中提供用戶認證相關的變數（如 user 物件、perms 等）
                'django.contrib.messages.context_processors.messages',# 在模板中提供一次性訊息相關的變數（如 messages 物件）
            ],
        },
    },
]

# 指定 WSGI 應用程式的入口點，這是供伺服器 (如 Gunicorn/uWSGI) 呼叫 Django 的介面
WSGI_APPLICATION = 'oracle_monitor.wsgi.application'

# -----------------------------------------------------------------------------
# 資料庫設定 (Database)
# -----------------------------------------------------------------------------
# 這裡清空了 Django 預設的資料庫設定，代表此專案完全不使用 Django 的內建 ORM。
# 原因：Oracle 的連線管理將會交由 oracledb 套件來直接控管，不依賴 Django db engine。
#DATABASES = {}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
}

# -----------------------------------------------------------------------------
# 靜態檔案設定 (Static files)
# -----------------------------------------------------------------------------
# 網頁中讀取靜態檔案 (CSS/JS) 時的 URL 前綴
STATIC_URL = '/static/'
# 開發時 Django 會去哪裡找額外的靜態檔案目錄
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# 執行 collectstatic 指令時，所有收集到的靜態檔案集中存放的路徑 (正式環境部署用)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# -----------------------------------------------------------------------------
# 國際化與語系時間設定
# -----------------------------------------------------------------------------
LANGUAGE_CODE = 'zh-hant' # 預設語系：繁體中文
TIME_ZONE = 'Asia/Taipei' # 預設時區：台北時間 (UTC+8)
USE_I18N = True           # 啟用國際化 (多語系) 翻譯系統
USE_TZ = True             # 啟用時區感知時間 (讓 Date/Time 儲存時具有時區概念)

# -----------------------------------------------------------------------------
# 暫存與 Session 設定 (Cache & Session)
# -----------------------------------------------------------------------------
# 因為我們把資料庫 (DATABASES) 清空了，所以使用預設的 DB based session 會報錯。
# 這裡將 Session 改成儲存於本機記憶體 (Cache) 中。
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# 配置 Django 預設的快取引擎使用本機記憶體 Cache (LocMemCache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# 動態將 SessionMiddleware 插入至 MIDDLEWARE 串列的第 2 個位置 (index 1)。
# session 管理必須在此位置，因為它依賴 SecurityMiddleware，又需在 CSRF 或 Common 前處理。
#MIDDLEWARE.insert(1, 'django.contrib.sessions.middleware.SessionMiddleware')

# Logging 日誌設定
# 集中管理應用程式與 Django 的日誌輸出，方便在終端機或容器日誌中進行查看與除錯
LOGGING = {
    'version': 1,                         # 目前 Python dictConfig 唯一支援的版本就是 1
    'disable_existing_loggers': False,    # 設為 False 確保不會覆蓋或停用 Django 預設內建的日誌記錄器
    'formatters': {
        'verbose': {
            # 定義日誌的輸出格式：[時間] 記錄級別 模組名稱: 詳細訊息
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            # 將日誌輸出到標準輸出 (Console / Terminal)
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',       # 套用上方定義的 verbose 格式
        },
    },
    'root': {
        # 根記錄器 (Root Logger)，全域捕捉所有應用程式與套件的日誌
        'handlers': ['console'],          # 將所有捕捉到的日誌交由 console 輸出
        'level': 'INFO',                  # 只顯示 INFO (含)以上級別的日誌 (包含 INFO, WARNING, ERROR, CRITICAL)
    },
}

# -----------------------------------------------------------------------------
# 自訂變數
# -----------------------------------------------------------------------------
DEFAULT_DB_HOST = os.getenv('DEFAULT_DB_HOST', 'localhost')
print(f"預設資料庫主機: {DEFAULT_DB_HOST}")
