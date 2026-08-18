from app.ai.agent import (
    booking_analysis_graph,
    daily_summary_graph,
    recommend_upsell,
)


def test_booking_langgraph_structure():
    nodes = set(booking_analysis_graph.nodes)

    assert "assess_priority" in nodes
    assert "detect_conflict" in nodes
    assert "recommend_upsell" in nodes
    assert "compose_confirmation" in nodes
    assert "persist_booking_analysis" in nodes


def test_daily_summary_langgraph_structure():
    nodes = set(daily_summary_graph.nodes)

    assert "collect_metrics" in nodes
    assert "compose_summary" in nodes
    assert "create_recommendations" in nodes
    assert "persist_summary" in nodes


def test_langchain_upsell_tool():
    result = recommend_upsell.invoke(
        {"service_name": "Haircut"}
    )

    assert result == "Add a wash and styling finish"
