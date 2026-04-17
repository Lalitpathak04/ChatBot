import streamlit as st
from langgraph_backend import get_chatbot, retrieve_all_threads, save_thread
from langchain_core.messages import HumanMessage, AIMessage
import uuid

chatbot = get_chatbot()

# ===================== Utilities =====================

def generate_thread_id():
    return str(uuid.uuid4())

def new_chat():
    tid = generate_thread_id()

    save_thread(tid)   # 👈 persist thread

    st.session_state.thread_id = tid
    st.session_state.messages = []
    st.session_state.chat_threads = retrieve_all_threads()

def load_chat(tid):
    st.session_state.thread_id = tid

    state = chatbot.get_state(
        {"configurable": {"thread_id": tid}}
    )

    if state and "history" in state.values:
        st.session_state.messages = [
            {
                "role": "user" if m.type == "human" else "assistant",
                "content": m.content
            }
            for m in state.values["history"]
        ]
    else:
        st.session_state.messages = []

# ===================== Page =====================

st.set_page_config(page_title="AI Assistant", layout="centered")
st.title("💬 LangGraph Chatbot")

# ===================== Session =====================

if "thread_id" not in st.session_state:
    tid = generate_thread_id()
    save_thread(tid)
    st.session_state.thread_id = tid

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_threads" not in st.session_state:
    st.session_state.chat_threads = retrieve_all_threads()

# ===================== Config =====================

CONFIG = {"configurable": {"thread_id": st.session_state.thread_id}}

# ===================== Sidebar =====================

st.sidebar.title("LangGraph Chatbot")

st.sidebar.button("➕ New Chat", on_click=new_chat)

st.sidebar.header("My Conversations")

for tid in st.session_state.chat_threads:
    st.sidebar.button(
        tid[:8],
        key=tid,
        on_click=load_chat,
        args=(tid,)
    )

# ===================== Chat =====================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("What is on your mind?"):

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            output = chatbot.invoke(
                {"history": [HumanMessage(content=prompt)]},
                config=CONFIG
            )

            
             #new
            #state = chatbot.get_state(CONFIG)
            #reply = state.values["history"][-1].content

            reply = output["history"][-1].content

            st.markdown(reply)

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
