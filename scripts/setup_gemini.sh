#!/bin/bash
# 設定 Gemini API Key 環境變數

echo "🤖 **Gemini API Key 設定**"
echo "=========================="

# 檢查是否已設定
if [ -n "$GEMINI_API_KEY" ]; then
    echo "✅ 環境變數 GEMINI_API_KEY 已設定"
    echo "   值: ${GEMINI_API_KEY:0:10}..."
else
    echo "❌ 環境變數 GEMINI_API_KEY 未設定"
    echo ""
    echo "請按照以下步驟設定："
    echo "1. 前往 https://makersuite.google.com/app/apikey"
    echo "2. 登入 Google 帳戶"
    echo "3. 點擊 'Create API key in new project'"
    echo "4. 複製 API Key"
    echo "5. 執行以下命令："
    echo "   export GEMINI_API_KEY='your-api-key-here'"
    echo ""
    echo "或者將以下內容加入 ~/.bashrc 或 ~/.zshrc："
    echo "export GEMINI_API_KEY='your-api-key-here'"
fi

echo ""
echo "🧪 **測試 Gemini API**"
echo "====================="

# 如果已設定，執行測試
if [ -n "$GEMINI_API_KEY" ]; then
    python3 scripts/test_gemini_integration.py
else
    echo "請先設定 GEMINI_API_KEY 環境變數"
fi

