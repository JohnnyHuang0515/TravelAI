import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# 修正 sys.path
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.itinerary_planner.main import app
from src.itinerary_planner.domain.models.itinerary import Itinerary

client = TestClient(app)

@pytest.fixture
def mock_clients():
    """Mock 掉所有外部依賴"""
    with patch('src.itinerary_planner.application.graph_nodes.llm_client') as mock_llm, \
         patch('src.itinerary_planner.application.graph_nodes.osrm_client') as mock_osrm, \
         patch('src.itinerary_planner.application.graph_nodes.embedding_client') as mock_embed, \
         patch('src.itinerary_planner.application.services.feedback_parser.llm_client') as mock_feedback_llm:
        
        # Mock LLM for story extraction
        mock_story = MagicMock()
        mock_story.days = 2
        mock_story.preference.themes = ["美食"]
        mock_llm.extract_story_from_text.return_value = mock_story

        # Mock OSRM
        mock_osrm.get_travel_time_matrix.return_value = [[0, 600], [600, 0]] # 10 minutes

        # Mock Embedding
        mock_embed.get_embedding.return_value = [0.1] * 384

        yield mock_llm, mock_osrm, mock_embed, mock_feedback_llm


def test_full_planning_and_feedback_flow(mock_clients, setup_db):
    """
    測試一次完整的端到端流程：
    1. 使用者發送請求生成行程。
    2. 使用者對生成的行程提出修改回饋。
    3. 驗證回饋是否被正確處理。
    """
    # --- 步驟 1: 提出初始建議 ---
    propose_request = {
        "session_id": "test-session-123",
        "text": "我想去宜蘭玩兩天，喜歡美食"
    }
    
    # 由於我們 mock 了 LLM 和 OSRM，這裡會觸發模擬的 LangGraph 流程
    # 但資料庫查詢是真實的 (使用 setup_db fixture)
    response_propose = client.post("/v1/itinerary/propose", json=propose_request)
    
    assert response_propose.status_code == 200
    itinerary_data = response_propose.json()
    
    # 驗證初始行程是否符合預期 (基於 test_places_api.py 中的資料)
    # 假設 greedy planner 會選擇 "Another Restaurant" 和 "Test Restaurant"
    assert len(itinerary_data["days"]) == 2
    # 這裡我們只做簡單驗證，因為詳細的 planner 邏輯應由單元測試覆蓋
    assert len(itinerary_data["days"][0]["visits"]) > 0 

    # --- 步驟 2: 提出修改回饋 ---
    
    # 轉換為 Pydantic 模型以便發送請求
    initial_itinerary = Itinerary(**itinerary_data)

    feedback_request = {
        "session_id": "test-session-123",
        "itinerary": initial_itinerary.model_dump(),
        "feedback_text": "第二天不要去了" # 假設這個指令會被解析
    }

    # Mock feedback parser 的 LLM (如果需要)
    mock_llm, _, _, mock_feedback_llm = mock_clients
    # 假設 feedback parser 會將指令解析為 DSL
    # (在我們的 feedback_parser.py 中，這是規則驅動的，所以不需要 mock LLM)

    response_feedback = client.post("/v1/itinerary/feedback", json=feedback_request)

    assert response_feedback.status_code == 200
    updated_itinerary_data = response_feedback.json()

    # --- 步驟 3: 驗證修改結果 ---
    # 根據我們的 feedback_parser 和 planning_service 實現，
    # "第二天不要去了" 應該會清空第二天的行程
    assert len(updated_itinerary_data["days"]) == 2
    assert len(updated_itinerary_data["days"][0]["visits"]) > 0 # 第一天不變
    assert len(updated_itinerary_data["days"][1]["visits"]) == 0 # 第二天被清空
