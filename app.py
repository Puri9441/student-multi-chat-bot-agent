import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv
from graph.workflow import build_student_support_graph

load_dotenv()

graph_app = build_student_support_graph()

st.set_page_config(page_title="Student Support Chatbot", page_icon="🎓", layout="wide")

# Database Status Check Function
def check_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "student_db")
        )
        if conn.is_connected():
            conn.close()
            return True
    except:
        return False
    return False

# Sidebar Configuration
st.sidebar.title("🛠 System Diagnostics")
student_id = st.sidebar.number_input("Student ID", value=101, step=1)

db_online = check_db_connection()
if db_online:
    st.sidebar.success("Database Status: Connected")
else:
    st.sidebar.error("Database Status: Disconnected")

st.sidebar.info(f"Model Name: llama3.2")

category_placeholder = st.sidebar.empty()
category_placeholder.metric(label="Active Category", value="N/A")

# Main Interface
st.title("🎓 Student Support Chatbot")
st.caption("AI powered student query and support system with session memory")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_query := st.chat_input("Ask your question here..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    state = {
        "user_query": user_query,
        "student_id": student_id,
        "category": None,
        "retrieved_info": None,
        "final_response": None,
        "chat_history": st.session_state.messages[:-1]  # Pass previous context
    }

    with st.chat_message("assistant"):
        with st.spinner("Processing your query..."):
            result = graph_app.invoke(state)
            response = result.get("final_response", "Sorry, no response generated.")
            category = result.get("category", "N/A")
            
            st.markdown(response)
            category_placeholder.metric(label="Active Category", value=category.upper())
            
    st.session_state.messages.append({"role": "assistant", "content": response})