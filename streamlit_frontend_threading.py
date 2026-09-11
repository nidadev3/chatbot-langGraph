import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessageChunk
import uuid


# ****** Utility Functions ******

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id


# Reset chat
def reset_chat():
    thread_id = generate_thread_id()

    st.session_state['thread_id'] = thread_id

    add_thread(st.session_state['thread_id'])

    st.session_state['message_history'] = []


# Load conversation from LangGraph
def load_conversation(thread_id):

    state = chatbot.get_state(
        config={
            'configurable': {
                'thread_id': thread_id
            }
        }
    )

    return state.values.get('messages', [])


# Add thread to chat_threads
def add_thread(thread_id):

    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)


# Extract clean text from message content
def get_message_text(content):

    # If content is already a normal string
    if isinstance(content, str):
        return content

    # If content is a list of blocks
    elif isinstance(content, list):

        text_parts = []

        for block in content:

            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))

        return "".join(text_parts)

    return str(content)


# ****** Session Setup ******

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()


if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []


# Add current thread
add_thread(st.session_state['thread_id'])


# ****** Sidebar UI ******

st.sidebar.title('LangGraph Chatbot')


# New Chat button
if st.sidebar.button('New Chat'):
    reset_chat()


st.sidebar.header('My Conversations')


# Display conversations
for thread_id in st.session_state['chat_threads'][::-1]:

    if st.sidebar.button(str(thread_id)):

        # Set selected thread as current thread
        st.session_state['thread_id'] = thread_id

        # Load messages from LangGraph
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:

            # Determine role
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'

            # Extract clean text
            content = get_message_text(msg.content)

            temp_messages.append({
                'role': role,
                'content': content
            })

        # Replace current message history
        st.session_state['message_history'] = temp_messages


# ****** Display Current Conversation ******

for message in st.session_state['message_history']:

    with st.chat_message(message['role']):
        st.text(message['content'])


# ****** Chat Input ******

user_input = st.chat_input('Type here')


if user_input:

    # Add user message to history
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })


    # Display user message
    with st.chat_message('user'):
        st.text(user_input)


    # LangGraph configuration
    CONFIG = {
        'configurable': {
            'thread_id': st.session_state['thread_id']
        }
    }


    # Display assistant response
    with st.chat_message("assistant"):

        def ai_only_stream():

            for message_chunk, metadata in chatbot.stream(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },
                config=CONFIG,
                stream_mode="messages"
            ):

                # Only process AI message chunks
                if isinstance(message_chunk, AIMessageChunk):

                    # Content is directly a string
                    if isinstance(message_chunk.content, str):

                        yield message_chunk.content

                    # Content is a list of blocks
                    elif isinstance(message_chunk.content, list):

                        for block in message_chunk.content:

                            if (
                                isinstance(block, dict)
                                and block.get("type") == "text"
                            ):
                                yield block.get("text", "")


        # Stream assistant response
        ai_message = st.write_stream(ai_only_stream())


    # Save assistant response to history
    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_message
    })