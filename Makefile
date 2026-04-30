# =========================================================
# Django + UV 開發工具 Makefile
# ---------------------------------------------------------
# 使用方式：
#   make help        查看所有指令
#   make run         本機對外啟動 Django
#   make migrate     執行資料庫遷移
# =========================================================

# 預設目標：直接輸入 make 時顯示說明
help: ## 顯示所有可用指令
	@uv run python help.py

# ---------------------------------------------------------
# Django Server
# ---------------------------------------------------------

run: ## 對外啟動 Django (0.0.0.0:8000)
	uv run python manage.py runserver 0.0.0.0:8000

run.dev: ## 僅本機開發模式 (127.0.0.1)
	uv run python manage.py runserver


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------
migrate: ## 套用資料庫 migration
	uv run python manage.py migrate

makemigrations: ## 產生新的 migration 檔案
	uv run python manage.py makemigrations

adduser: ## 建立 Django 管理員帳號
	uv run python manage.py createsuperuser

# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------
test: ## 執行 pytest 測試
	uv run pytest


# ---------------------------------------------------------
# Lint / Format
# ---------------------------------------------------------
lint: ## 程式碼檢查 (ruff)
	uv run ruff check .

format: ## 自動修復程式碼風格
	uv run ruff check . --fix

# ---------------------------------------------------------
# UV tools
# ---------------------------------------------------------

tree: ## 顯示 Python 套件依賴樹
	uv tree