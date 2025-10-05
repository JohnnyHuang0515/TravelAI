# uv 專案管理指南

本專案已轉換為使用 uv 進行 Python 專案管理，遵循 uv 專案管理規範 v1.0。

## 📋 目錄

- [安裝 uv](#安裝-uv)
- [快速開始](#快速開始)
- [常用指令](#常用指令)
- [專案結構](#專案結構)
- [開發工作流程](#開發工作流程)
- [故障排除](#故障排除)

## 🚀 安裝 uv

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```

## ⚡ 快速開始

### 新成員或新機器設定

```bash
# 克隆專案
git clone <repository-url>
cd TravelAI

# 同步依賴（會自動建立 .venv）
uv sync

# 驗證環境
uv run python --version  # 應該顯示 Python 3.10.0
uv run python -c "import fastapi; print('環境設定成功！')"
```

### 日常開發

```bash
# 啟動開發服務器
uv run python start_server.py

# 執行測試
uv run pytest tests/

# 執行腳本
uv run python scripts/init_database.py
```

## 🛠️ 常用指令

### 依賴管理

```bash
# 新增依賴
uv add fastapi
uv add "requests>=2.31.0"

# 新增開發依賴
uv add --dev pytest
uv add --dev ruff

# 移除依賴
uv remove requests

# 批次新增（從 requirements.txt）
uv add -r requirements.txt

# 查看依賴樹
uv tree

# 更新依賴
uv lock --upgrade
uv sync
```

### 虛擬環境管理

```bash
# 建立虛擬環境
uv venv

# 使用特定 Python 版本建立環境
uv venv --python 3.10.0

# 同步依賴到環境
uv sync

# 在環境中執行指令
uv run <command>
```

### Python 版本管理

```bash
# 安裝 Python 版本
uv python install 3.10.0

# 列出可用版本
uv python list

# 使用特定版本建立環境
uv venv --python 3.10.0
```

### 全域工具安裝

```bash
# 安裝全域工具（取代 pipx）
uv tool install ruff
uv tool install black
uv tool install mypy

# 列出已安裝工具
uv tool list

# 移除工具
uv tool uninstall ruff
```

## 📁 專案結構

```
TravelAI/
├── src/                    # 後端源碼
├── frontend/              # 前端應用
├── scripts/               # 工具腳本
├── tests/                 # 測試檔案
├── docs/                  # 文件
├── pyproject.toml         # 專案配置（依賴、工具設定）
├── uv.lock               # 依賴鎖定檔（提交到版本控制）
├── .venv/                # 虛擬環境（不提交）
├── .gitignore            # Git 忽略規則
└── requirements.txt       # 舊版依賴檔（保留作為參考）
```

## 🔄 開發工作流程

### 1. 日常開發

```bash
# 啟動開發
uv run python start_server.py

# 執行測試
uv run pytest tests/

# 程式碼檢查
uv run ruff check src/
uv run black --check src/
uv run mypy src/
```

### 2. 新增功能

```bash
# 新增依賴
uv add new-package

# 測試新功能
uv run pytest tests/test_new_feature.py

# 提交變更
git add pyproject.toml uv.lock
git commit -m "feat: 新增功能"
```

### 3. 更新依賴

```bash
# 更新所有依賴
uv lock --upgrade
uv sync

# 測試更新後的功能
uv run pytest tests/

# 提交更新
git add uv.lock
git commit -m "chore: 更新依賴"
```

## 🔧 工具配置

### pyproject.toml 配置

專案的 `pyproject.toml` 包含：

- **專案資訊**: 名稱、版本、描述
- **依賴管理**: 主要依賴和可選依賴
- **工具設定**: ruff、black、mypy、pytest 配置
- **建置設定**: hatchling 建置後端

### 開發工具

```bash
# 程式碼格式化
uv run black src/

# 程式碼檢查
uv run ruff check src/
uv run ruff format src/

# 型別檢查
uv run mypy src/

# 測試執行
uv run pytest tests/ -v
uv run pytest tests/ --cov=src
```

## 🚨 故障排除

### 常見問題

#### 1. uv: command not found

```bash
# 確認 PATH 設定
echo $PATH

# 重新安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # 或 ~/.zshrc
```

#### 2. 依賴編譯失敗

```bash
# 更新到最新版本
uv lock --upgrade
uv sync

# 或使用特定 Python 版本
uv venv --python 3.10.0
uv sync
```

#### 3. 版本不符

```bash
# 安裝所需版本
uv python install 3.10.0

# 重建環境
rm -rf .venv
uv venv --python 3.10.0
uv sync
```

#### 4. 依賴飄移

```bash
# 重新鎖定依賴
uv lock

# 同步到環境
uv sync

# 提交變更
git add uv.lock
git commit -m "fix: 修正依賴版本"
```

### 環境重置

```bash
# 完全重置環境
rm -rf .venv
uv venv --python 3.10.0
uv sync
```

## 📚 參考資料

- [uv 官方文件](https://docs.astral.sh/uv/)
- [uv 專案管理規範](https://docs.astral.sh/uv/project-management/)
- [pyproject.toml 規範](https://packaging.python.org/en/latest/specifications/pyproject-toml/)

## ✅ 檢查清單

- [ ] 已安裝 uv 並可執行
- [ ] 專案已建立 .venv
- [ ] 依賴以 uv add 管理
- [ ] 已產生並提交 uv.lock
- [ ] .venv、.env 未提交到版本控制
- [ ] 開發工具正常運作
- [ ] 測試可以正常執行
