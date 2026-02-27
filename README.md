🤖 ChatBot
An intelligent, state-aware conversational assistant built with LangGraph and Streamlit. It combines the power of OpenAI's LLMs with real-time web search to provide accurate, context-aware answers.

Live Demo | Report Bug

🚀 Features
Agentic Workflow: Uses LangGraph for complex, multi-turn dialogue management.

Real-time RAG: Integrated with Tavily Search and BeautifulSoup4 for live web retrieval.

Session Persistence: Maintains chat history and state across interactions.

Modern UI: Clean, responsive interface powered by Streamlit.

🛠️ Tech Stack
Frameworks: LangChain, LangGraph, Streamlit

AI Models: OpenAI GPT

Tools: Tavily AI (Search), BeautifulSoup4 (Parsing)

⚡ Quick Start
1. Clone & Install

Bash
git clone https://github.com/Lalitpathak04/ChatBot.git
cd ChatBot
pip install -r requirements.txt
2. Configure Environment
Create a .env file in the root:

Code snippet
OPENAI_API_KEY="your_key"
TAVILY_API_KEY="your_key"
3. Run

Bash
streamlit run streamlit_frontend.py
📂 Structure
langgraph_backend.py: Core agent logic and graph definition.

streamlit_frontend.py: UI and session handling.

requirements.txt: Project dependencies.

Built with ❤️ by Lalit
