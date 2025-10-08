from langgraph.graph import StateGraph, END
from .graph_state import AppState
from .graph_nodes import GraphNodes

# 建立節點實例
nodes = GraphNodes()

# 建立圖
workflow = StateGraph(AppState)

# 定義節點 - 新增對話式節點
workflow.add_node("conversation_memory_manager", nodes.conversation_memory_manager)
workflow.add_node("info_collector", nodes.info_collector)
workflow.add_node("extract_story", nodes.extract_story)
workflow.add_node("retrieve_structured", nodes.retrieve_places_structured)
workflow.add_node("retrieve_semantic", nodes.retrieve_places_semantic)
workflow.add_node("rank_and_merge", nodes.rank_and_merge)
workflow.add_node("retrieve_accommodations", nodes.retrieve_accommodations)
workflow.add_node("plan_itinerary", nodes.plan_itinerary)

# 設定圖的邊 - 支援對話式流程
workflow.set_entry_point("conversation_memory_manager")
workflow.add_edge("conversation_memory_manager", "info_collector")

# 條件分支：如果資訊完整則進入規劃，否則結束對話
def should_continue_collecting(state: AppState) -> str:
    """決定是否繼續收集資訊"""
    print("=" * 80)
    print("🔍 **CONDITIONAL BRANCH: should_continue_collecting**")
    print("=" * 80)
    print(f"📊 檢查狀態: {state}")
    
    is_complete = state.get("is_info_complete", False)
    print(f"✅ 資訊完整性: {is_complete}")
    
    if is_complete:
        print("🎯 資訊完整，進入 extract_story")
        result = "extract_story"
    else:
        print("❓ 資訊不完整，結束對話")
        result = "end_conversation"
    
    print(f"📤 返回結果: {result}")
    print("=" * 80)
    
    return result

workflow.add_conditional_edges(
    "info_collector",
    should_continue_collecting,
    {
        "extract_story": "extract_story",
        "end_conversation": END
    }
)

# 原有的規劃流程
workflow.add_edge("extract_story", "retrieve_structured")
workflow.add_edge("retrieve_structured", "retrieve_semantic")
workflow.add_edge("retrieve_semantic", "rank_and_merge")
workflow.add_edge("rank_and_merge", "retrieve_accommodations")
workflow.add_edge("retrieve_accommodations", "plan_itinerary")
workflow.add_edge("plan_itinerary", END)

# 編譯圖
app_graph = workflow.compile()

print("✅ LangGraph 對話式行程規劃應用編譯成功！")
print("🔄 支援多輪對話收集資訊")
print("🎯 基於收集資訊生成個性化行程")
