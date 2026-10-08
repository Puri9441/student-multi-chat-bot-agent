from typing import TypedDict, Optional, List, Dict

class AgentState(TypedDict):
    user_query: str
    student_id: Optional[int]
    category: Optional[str]
    retrieved_info: Optional[str]
    final_response: Optional[str]
    chat_history: Optional[List[Dict[str, str]]]

class AgentState(TypedDict):
    user_query: str
    student_id: Optional[int]
    category: Optional[str]
    retrieved_info: Optional[str]
    final_response: Optional[str]
    chat_history: Optional[List[Dict[str, str]]]