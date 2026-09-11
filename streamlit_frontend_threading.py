import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid


#******utility finctions******

def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id





# ***********SideBar UI***********

st.sidebar.title('LangGraph Chatbot')

st.sidebar.button('New Chat')