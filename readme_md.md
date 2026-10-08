# 🎓 Multi-Agent Student Support Chatbot System

An AI-powered multi-agent student query and support system built using **LangGraph**, **Ollama (Llama 3.2)**, **Pinecone**, **MySQL**, and **Streamlit**. 

This application uses conditional routing to dynamically guide incoming student queries to specialized processing nodes—such as checking database payment balances, retrieving course syllabi from a vector knowledge base, submitting support tickets, or probing real-time external APIs.

---

## 🌟 Architecture & Workflow

```
                        +-------------------+
                        |   User Query      |
                        +---------+---------+
                                  |
                                  v
                        +-------------------+
                        |  Classifier Node  |
                        +---------+---------+
                                  |
            +---------------------+---------------------+---------------------+
            |                     |                     |                     |
            v                     v                     v                     v
    +---------------+     +---------------+     +---------------+     +---------------+
    | Database Node |     |   RAG Node    |     |   API Node    |     |Complaint Node |
    | (MySQL Fees)  |     | (Pinecone VDB)|     | (Live Web/API)|     |(MySQL Ticket) |
    +-------+-------+     +-------+-------+     +-------+-------+     +-------+-------+
            |                     |                     |                     |
            +---------------------+---------------------+---------------------+
                                  |
                                  v
                        +-------------------+
                        |   Answer Node     |
                        |   (Llama 3.2)     |
                        +---------+---------+
                                  |
                                  v
                        +-------------------+
                        |  Streamlit UI     |
                        +-------------------+
```

### Key Agent Nodes
1. **`classifier_node`**: Analyzes intent and routes the query to the correct processing node.
2. **`database_node`**: Connects to MySQL (`payments` table) to query student tuition fees, balances, and payment histories.
3. **`rag_node`**: Performs vector search using **Pinecone** and **Nomic Embed Text** to query embedded course syllabi and academic documents.
4. **`api_node`**: Fetches live data from external Web APIs (e.g., campus weather, server status probes).
5. **`complaint_node`**: Logs support requests into the MySQL (`complaints` table) and returns an auto-generated Ticket ID (e.g., `#TKT-1`).
6. **`answer_node`**: Synthesizes the retrieved context into a polite, concise, and structured student response using **Llama 3.2**.

---

## 🛠️ Tech Stack

* **Orchestration**: LangGraph, LangChain
* **LLM**: Ollama (`llama3.2`)
* **Embeddings**: Ollama (`nomic-embed-text`)
* **Vector Database**: Pinecone Serverless
* **Relational Database**: MySQL (`student_db`)
* **Frontend**: Streamlit
* **Language/Environment**: Python 3.10+

---

## 📁 Project Structure

```text
student_chat_bot/
├── app.py                     # Streamlit web application frontend
├── ingest_docs.py             # Script to split & upsert text documents to Pinecone
├── docs/                      # Text files containing curriculum/course syllabi
│   ├── data-structures.txt
│   ├── machine-learning.txt
│   └── web-development.txt
├── database/
│   ├── db_connection.py       # MySQL database connector
│   └── mysql_client.py        # Payment queries & complaint registration logic
├── graph/
│   ├── state.py               # LangGraph AgentState definition
│   ├── nodes.py               # Implementation of all agent nodes
│   └── workflow.py            # LangGraph routing logic and graph compilation
├── .env                       # Environment variables (API Keys, DB Credentials)
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## ⚡ Setup & Installation

### 1. Prerequisites
* **Python 3.10+** installed.
* **MySQL Server** running locally or remotely.
* **Ollama** installed locally with models pulled:
  ```bash
  ollama pull llama3.2
  ollama pull nomic-embed-text
  ```

### 2. Environment Setup
Clone the repository and create a virtual environment:
```bash
git clone https://github.com/your-username/student-support-chatbot.git
cd student-support-chatbot

python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables (`.env`)
Create a `.env` file in the project root:
```env
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=student-rag-index

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=student_db
```

### 4. Database Setup
Run the following queries in MySQL Workbench or Command Line to initialize `student_db`:

```sql
CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100),
    total_fee DECIMAL(10,2),
    paid_amount DECIMAL(10,2),
    due_amount DECIMAL(10,2),
    payment_status VARCHAR(50)
);

-- Complaints Table
CREATE TABLE IF NOT EXISTS complaints (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    issue_description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Sample Payment Data
INSERT INTO payments (student_id, student_name, total_fee, paid_amount, due_amount, payment_status)
VALUES (101, 'Srinivas', 50000.00, 35000.00, 15000.00, 'Partial')
ON DUPLICATE KEY UPDATE student_name=VALUES(student_name);
```

### 5. Ingest Knowledge Base into Pinecone
Add your syllabus or course `.txt` files into the `docs/` folder, then run:
```bash
python ingest_docs.py
```

---

## 🚀 Running the Application

Launch the Streamlit UI:
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🧪 Sample Queries to Test

| Intent | Sample Query | Target Node |
| :--- | :--- | :--- |
| **Payment Inquiry** | *"What is my current fee balance?"* | `database_node` |
| **Syllabus / Course** | *"What topics are covered in Data Structures Unit 2?"* | `rag_node` |
| **Support Ticket** | *"My payment failed but amount got debited, please log a complaint."* | `complaint_node` |
| **API / Status** | *"What is the campus weather status right now?"* | `api_node` |

---

## 📜 License
This project is open-source and available under the **MIT License**.