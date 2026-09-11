import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid


#******utility finctions******

def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id


def add_thread (thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_threads'].append(thread_id)



# ***********SideBar UI***********

st.sidebar.title('LangGraph Chatbot')

st.sidebar.button('New Chat')

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'] [::-1]:
    if st.sidebar.button(str[thread_id]):
        st.session_state['thread-id']=thread_id