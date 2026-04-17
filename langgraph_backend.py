import streamlit as st
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage, AnyMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import sqlite3

DB_PATH = "chatbot_memory.db"

# ===================== Model Initialization =====================
load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")


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

# ===================== Tools =====================


#search_tool = DuckDuckGoSearchRun(region="us", safesearch="Off")
@tool
def web_search(query: str):
    """Search the web for current events."""
    search_tool = DuckDuckGoSearchRun(region="us", safesearch="Off")
    result = search_tool.run(query)
    return result

@tool
def calculator_tool(first: float, second: float, operation: str) -> dict:
    """Performs basic arithmetic operations on two numbers. Supported operations are: add, subtract, multiply, divide."""
    if operation == "add":
        return first + second
    elif operation == "subtract":
        return first - second
    elif operation == "multiply":
        return first * second
    elif operation == "divide":
        return first / second
    else:
        raise ValueError("Unsupported operation")
    

all_tools = [web_search, calculator_tool]



model_with_tools = model.bind_tools(all_tools)
# ===================== LangGraph State =====================

class ChatState(TypedDict):
    history: Annotated[list[AnyMessage], add_messages]

def chat_node(state: ChatState):
    response = model_with_tools.invoke(state["history"])
    return {"history": [response]}

tools_node = ToolNode(all_tools, messages_key='history')


def custom_tools_condition(state: ChatState):
    last_message = state["history"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools_node"

    if "tool_calls" in getattr(last_message, "additional_kwargs", {}):
        return "tools_node"

    return "__end__"

# ===================== Graph =====================

@st.cache_resource
def get_chatbot():
    load_dotenv()
    init_thread_table()

    workflow = StateGraph(ChatState)
    workflow.add_node("chat_node", chat_node)
    workflow.add_node("tools_node", tools_node)
    
    workflow.add_edge(START, "chat_node")
    workflow.add_conditional_edges("chat_node", custom_tools_condition)
    workflow.add_edge("tools_node", 'chat_node')

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    memory = SqliteSaver(conn=conn)

    return workflow.compile(checkpointer=memory)
