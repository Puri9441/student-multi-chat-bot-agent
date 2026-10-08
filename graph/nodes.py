import os
import requests
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_ollama import ChatOllama, OllamaEmbeddings
from graph.state import AgentState
from database.mysql_client import fetch_payment_details, log_complaint

load_dotenv()

llm = ChatOllama(model="llama3.2")
embeddings = OllamaEmbeddings(model="nomic-embed-text")
index_name = os.getenv("PINECONE_INDEX_NAME", "student-rag-index")


def classifier_node(state: AgentState) -> AgentState:
    query = state["user_query"].lower()
    
    # 1. Complaint intent gets top priority
    if any(k in query for k in ["failed", "complaint", "issue", "problem", "ticket", "refund", "deducted", "wrong"]):
        category = "complaint"
    elif any(k in query for k in ["fee", "tuition", "payment", "due", "paid", "balance", "amount"]):
        category = "payment"
    elif any(k in query for k in ["syllabus", "course", "curriculum", "subject", "unit", "credits", "instructor", "prerequisites"]):
        category = "course"
    elif any(k in query for k in ["server", "portal", "api", "system", "working", "status", "uptime", "down"]):
        category = "api_status"
    else:
        category = "complaint"
        
    state["category"] = category
    return state




def database_node(state: AgentState) -> AgentState:
    student_id = state.get("student_id", 101)
    payment_info = fetch_payment_details(int(student_id))
    state["retrieved_info"] = payment_info
    return state


def rag_node(state: AgentState) -> AgentState:
    query = state["user_query"]
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(index_name)
        
        query_vector = embeddings.embed_query(query)
        response = index.query(vector=query_vector, top_k=3, include_metadata=True)
        
        matches = response.get("matches", [])
        if matches:
            retrieved_content = "\n\n".join([m["metadata"]["text"] for m in matches if "metadata" in m and "text" in m["metadata"]])
            state["retrieved_info"] = f"Pinecone Knowledge Base Context:\n{retrieved_content}"
        else:
            state["retrieved_info"] = "No relevant course syllabus details found in Pinecone."
            
    except Exception as e:
        state["retrieved_info"] = f"Error querying Pinecone DB: {str(e)}"
        
    return state




import requests
from graph.state import AgentState

def api_node(state: AgentState) -> AgentState:
    # Example: Open-Meteo free public API for Hyderabad weather updates
    url = "https://api.open-meteo.com/v1/forecast?latitude=17.3850&longitude=78.4867&current_weather=true"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data.get("current_weather", {})
            temp = current.get("temperature")
            wind = current.get("windspeed")
            
            state["retrieved_info"] = f"Live Weather Update for Hyderabad campus:\nTemperature: {temp}°C, Wind Speed: {wind} km/h"
        else:
            state["retrieved_info"] = "Failed to fetch live updates from website API."
    except Exception as e:
        state["retrieved_info"] = f"Error connecting to website API: {str(e)}"
        
    return state

def complaint_node(state: AgentState) -> AgentState:
    student_id = state.get("student_id", 101)
    query = state["user_query"]
    ticket_result = log_complaint(int(student_id), query)
    state["retrieved_info"] = ticket_result
    return state

def answer_node(state: AgentState) -> AgentState:
    query = state["user_query"]
    info = state.get("retrieved_info", "")
    history = state.get("chat_history", [])
    
    history_text = ""
    if history:
        for msg in history[-4:]:
            history_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
    
    prompt = f"""You are an automated Student Support AI Assistant.
Respond directly, politely, and concisely to the student using strictly the provided Context Information.

Rules:
- Do NOT include any placeholders like [Your Name], [Company Name], or sign-offs at the end.
- State relevant ticket IDs, payment status, or course details clearly.

Context Information:
{info}

Previous Chat History:
{history_text}

User Query: {query}
Response:"""

    response = llm.invoke(prompt).content.strip()
    state["final_response"] = response
    return state