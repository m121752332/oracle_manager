#!/bin/bash
# =============================================================
# Oracle Manager — 部署腳本
# OS: Red Hat Enterprise Linux 6.6
# Python: 3.7
# =============================================================

set -e

echo "======================================"
echo "  Oracle Manager 部署腳本"
echo "  RHEL 6.6 / Python 3.7"
echo "======================================"

# ── 1. 建立虛擬環境 ──────────────────────────────
echo ""
echo "[1/5] 準備虛擬環境工具 uv..."
# 安裝 uv (如果環境沒有的話)，並建立環境
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

echo "建立 Python 虛擬環境..."
uv venv .venv

# ── 2. 安裝依賴 ──────────────────────────────────
echo ""
echo "[2/5] 同步安裝 Python 套件..."
uv sync

echo " -> make tree看一下依賴樹..."
make tree

echo ""
echo "      ⚠  若需連線真實 Oracle，請另外安裝 oracledb："
echo "         uv pip install oracledb"
echo "         並確認 Oracle Instant Client 已安裝於："
echo "         /u2/oracle/product/11.2.0/dbhome_1/lib"

# ── 3. 設定環境變數 ──────────────────────────────
echo ""
echo "[3/5] 設定環境變數..."
cat > .env << 'EOF'
# Oracle Manager 環境設定
# 正式部署請修改以下設定

DJANGO_SETTINGS_MODULE=oracle_monitor.settings
# 若正式環境請設定強密碼
DJANGO_SECRET_KEY=change-this-to-random-string-in-production

# Oracle Instant Client 路徑（依實際安裝調整）
# LD_LIBRARY_PATH=/u2/oracle/product/11.2.0/dbhome_1/lib:$LD_LIBRARY_PATH
EOF

echo "      .env 已產生，請依需求修改"

# ── 4. collectstatic ─────────────────────────────
echo ""
echo "[4/5] 收集靜態檔案..."
python manage.py collectstatic --noinput 2>/dev/null || true

# ── 5. 啟動說明 ──────────────────────────────────
echo ""
echo "[5/5] 部署完成！"
echo ""
echo "======================================"
echo "  啟動方式"
echo "======================================"
echo ""
echo "  【開發模式】"
echo "  make run.dev"
echo "  # 或手動啟動： python manage.py runserver 0.0.0.0:8000"
echo ""
echo "  【生產模式 (gunicorn)】"
echo "  source .venv/bin/activate"
echo "  gunicorn oracle_monitor.wsgi:application \\"
echo "    --bind 0.0.0.0:8000 \\"
echo "    --workers 2 \\"
echo "    --timeout 60 \\"
echo "    --access-logfile access.log \\"
echo "    --error-logfile error.log \\"
echo "    --daemon"
echo ""
echo "  瀏覽器開啟: http://<server-ip>:8000"
echo ""
echo "  【oracledb 前置需求】"
echo "  1. 安裝 Oracle Instant Client Basic"
echo "     rpm -ivh oracle-instantclient19.8-basic-*.rpm"
echo "  2. 設定 LD_LIBRARY_PATH"
echo "     export LD_LIBRARY_PATH=/usr/lib/oracle/19.8/client64/lib"
echo "  3. 安裝 oracledb"
echo "     uv add oracledb"
echo "======================================"
