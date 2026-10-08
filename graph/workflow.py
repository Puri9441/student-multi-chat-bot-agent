from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import (
    classifier_node,
    database_node,
    rag_node,
    api_node,
    complaint_node,
    answer_node
)

def route_intent(state: AgentState) -> str:
    category = state.get("category", "complaint")
    if category == "payment":
        return "database_node"
    elif category == "course":
        return "rag_node"
    elif category == "api_status":
        return "api_node"
    else:
        return "complaint_node"

def build_student_support_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("classifier_node", classifier_node)
    workflow.add_node("database_node", database_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("api_node", api_node)
    workflow.add_node("complaint_node", complaint_node)
    workflow.add_node("answer_node", answer_node)
    
    # Set entry point
    workflow.set_entry_point("classifier_node")
    
    # Conditional routing from classifier
    workflow.add_conditional_edges(
        "classifier_node",
        route_intent,
        {
            "database_node": "database_node",
            "rag_node": "rag_node",
            "api_node": "api_node",
            "complaint_node": "complaint_node"
        }
    )
    
    # Connect category nodes to answer node
    workflow.add_edge("database_node", "answer_node")
    workflow.add_edge("rag_node", "answer_node")
    workflow.add_edge("api_node", "answer_node")
    workflow.add_edge("complaint_node", "answer_node")
    workflow.add_edge("answer_node", END)
    
    return workflow.compile()