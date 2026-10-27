import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langgraph_tool_backend import (
    chatbot,
    retrieve_all_threads,
    save_thread_title,
    get_thread_title
)
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
import uuid


# ****** Utility Functions ******

def generate_thread_id():
    return str(uuid.uuid4())



def reset_chat():
    st.session_state['thread_id'] = generate_thread_id()
    st.session_state['message_history'] = []


# Load conversation from LangGraph
def load_conversation(thread_id):
    state = chatbot.get_state(
        config={'configurable': {'thread_id': thread_id}}
    )
    return state.values.get('messages', [])


# Add thread to chat_threads
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)


# Extract clean text from message content
def get_message_text(content):

    if isinstance(content, str):
        return content

    elif isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return "".join(text_parts)

    return str(content)


# Convert LangGraph messages into UI messages (only real user/assistant text)
def to_ui_messages(messages):

    ui_messages = []

    for msg in messages:

        if isinstance(msg, HumanMessage):
            role = 'user'
        elif isinstance(msg, AIMessage):
            role = 'assistant'
        else:
            continue  # ToolMessage etc. skip

        content = get_message_text(msg.content)

        if not content.strip():
            continue  # tool-call-only AI messages skip

        ui_messages.append({'role': role, 'content': content})

    return ui_messages



def get_display_title(thread_id):

    title = get_thread_title(thread_id)

    if title and title != "New Chat":
        return title

    msgs = to_ui_messages(load_conversation(thread_id))
    first_user = next((m['content'] for m in msgs if m['role'] == 'user'), None)

    if not first_user:
        return None

    t = first_user.strip().replace("\n", " ")
    t = t[:32] + "..." if len(t) > 35 else t

    save_thread_title(thread_id, t)
    return t


# Render one message in the UI
def render_message(role, content):
    with st.chat_message(role):
        if role == 'assistant':
            st.markdown(content)
        else:
            st.text(content)


# ****** Session Setup ******

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()


# ****** Sidebar UI ******

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()
    st.rerun()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:

    title = get_display_title(thread_id)

    if title is None:
        continue  # empty thread skip

    if st.sidebar.button(title, key=str(thread_id)):

        st.session_state['thread_id'] = thread_id

        messages = load_conversation(thread_id)
        st.session_state['message_history'] = to_ui_messages(messages)

        st.rerun()


# ****** Display Current Conversation ******

for message in st.session_state['message_history']:
    render_message(message['role'], message['content'])


# ****** Chat Input ******

user_input = st.chat_input('Type here')

if user_input:

    # Save title for new conversation
    messages = load_conversation(st.session_state['thread_id'])

    if not messages:
        title = user_input.strip().replace("\n", " ")

        if len(title) > 35:
            title = title[:32] + "..."

        save_thread_title(st.session_state['thread_id'], title)

    
    add_thread(st.session_state['thread_id'])

    # Add user message to history
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })

    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {
        'configurable': {'thread_id': st.session_state['thread_id']}
    }

    with st.chat_message("assistant"):

        def ai_only_stream():

            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):

                if isinstance(message_chunk, AIMessageChunk):

                    if isinstance(message_chunk.content, str):
                        yield message_chunk.content

                    elif isinstance(message_chunk.content, list):
                        for block in message_chunk.content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                yield block.get("text", "")

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_message
    })

    st.rerun()