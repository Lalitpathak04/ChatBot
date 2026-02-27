import streamlit as st
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import sqlite3

DB_PATH = "chatbot_memory.db"

# ===================== Thread Registry =====================

def init_thread_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            thread_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_thread(thread_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR IGNORE INTO threads (thread_id) VALUES (?)",
        (thread_id,)
    )
    conn.commit()
    conn.close()

def retrieve_all_threads():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT thread_id FROM threads ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]

# ===================== LangGraph State =====================

class ChatState(TypedDict):
    history: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    model = ChatGroq(model="llama-3.1-8b-instant")
    response = model.invoke(state["history"])
    return {"history": [response]}

# ===================== Graph =====================

@st.cache_resource
def get_chatbot():
    load_dotenv()
    init_thread_table()

    workflow = StateGraph(ChatState)
    workflow.add_node("chat_node", chat_node)
    workflow.add_edge(START, "chat_node")
    workflow.add_edge("chat_node", END)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    memory = SqliteSaver(conn=conn)

    return workflow.compile(checkpointer=memory)