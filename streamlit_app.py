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

agent_function_url = os.getenv("AGENT_FUNCTION")
if not agent_function_url:
    agent_function_url = st.secrets["AGENT_FUNCTION"]

agent_id = os.getenv("AGENT_ID")
if not agent_id:
    agent_id = st.secrets["AGENT_ID"]

language_code = os.getenv("LANGUAGE_CODE")
if not language_code:
    language_code = st.secrets["LANGUAGE_CODE"]

# Initialise session state variables
if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def process_user_input(query=None):
    user_input = query if query else st.session_state.user_input
    st.session_state["user_input"] = ""
    st.session_state.past.append(user_input)
    payload = {
        'token': sl_token,
        'agent_id': agent_id,
        'session_id': st.session_state.session_id,
        'query': user_input,
        'language_code': language_code
    }
    json_data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(agent_function_url, data=json_data, method='POST')
    request.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(request) as response:
        agent_response = response.read().decode('utf-8')
        st.session_state.generated.append({'type': 'normal', 'data': agent_response})

def new_session():
    del st.session_state.past[:]
    del st.session_state.generated[:]
    st.session_state["user_input"] = ""
    session_id = str(uuid.uuid4())
    st.session_state.session_id = session_id

st.sidebar.write("Example prompts:")

st.session_state.setdefault('past', [])
st.session_state.setdefault('generated', [])

example_button1 = st.sidebar.button("What are Sustainable Development Goals?")
if example_button1:
    process_user_input("What are Sustainable Development Goals?")

example_button2 = st.sidebar.button("Which is the Sustainable Development Goal 5?")
if example_button2:
    process_user_input("Which is the Sustainable DevelopmentGoal 5?")

example_button3 = st.sidebar.button("What is the Sustainable Development Goal 5 about?")
if example_button3:
    process_user_input("What is the Sustainable Development Goal 5 about?")

example_button4 = st.sidebar.button("Tell me an interesting fact about any Sustainable Development Goal of your choice")
if example_button4:
    process_user_input("Tell me an interesting fact about any any Sustainable Development Goal of your choice")

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

    st.button("New Conversation", on_click=new_session)

with st.container():
    st.text_input("User Input:", on_change=process_user_input, key="user_input")
