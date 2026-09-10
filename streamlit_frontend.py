import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIF={'configurable':{'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

# loading conversation fromm the history 

for message in st.session_state['message_history']:
    with st.chat_message('message_history'):
        st.text(message['content'])


