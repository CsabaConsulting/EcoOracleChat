import json
import os
import streamlit as st
import urllib.request
import uuid
from streamlit_chat import message

# https://pypi.org/project/streamlit-chat/
title = "Eco Oracle"
st.set_page_config(
    page_title=title,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set API keys
sl_token = os.getenv("SL_TOKEN")
if not sl_token:
    sl_token = st.secrets["SL_TOKEN"]

agent_url = os.getenv("AGENT_URL")
if not agent_url:
    agent_url = st.secrets["AGENT_URL"]

# Initialise session state variables
if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def process_user_input(query):
    user_input = query if query else st.session_state.user_input
    st.session_state.past.append(user_input)
    payload = {
        'token': sl_token,
        'session_id': st.session_state.session_id,
        'query': user_input
    }
    json_data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(agent_url, data=json_data, method='POST')
    request.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(request) as response:
        agent_response = response.read().decode('utf-8')
        st.session_state.generated.append(agent_response)

def clear_chat():
    del st.session_state.past[:]
    del st.session_state.generated[:]
    session_id = str(uuid.uuid4())
    st.session_state.session_id = session_id

# clear_button = st.sidebar.button("Clear Conversation", key="clear")
# if clear_button:
#     clear_chat()

st.sidebar.write("Example prompts:")

st.session_state.setdefault('past', [])
st.session_state.setdefault('generated', [])

example_button1 = st.sidebar.button("What are Sustainable Development Goals?")
if example_button1:
    process_user_input("What are Sustainable Development Goals?")

example_button2 = st.sidebar.button("Which is the SDG Goal 5?")
if example_button2:
    process_user_input("Which is the SDG Goal 5?")

example_button3 = st.sidebar.button("What is the SDG Goal 5 about?")
if example_button3:
    process_user_input("What is the SDG Goal 5 about?")

example_button4 = st.sidebar.button("Tell me an interesting fact about an SDG")
if example_button4:
    process_user_input("Tell me an interesting fact about an SDG")

chat_placeholder = st.empty()

with chat_placeholder.container():    
    for i in range(len(st.session_state['generated'])):                
        message(st.session_state['past'][i], is_user=True, key=f"{i}_user")
        message(
            st.session_state['generated'][i]['data'], 
            key=f"{i}", 
            allow_html=True,
            is_table=True if st.session_state['generated'][i]['type']=='table' else False
        )

    st.button("Clear message", on_click=clear_chat)

with st.container():
    st.text_input("User Input:", on_change=process_user_input, key="user_input")