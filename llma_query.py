import pickle
from pathlib import Path

import os
from dotenv import load_dotenv
import streamlit as st
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, Document
import streamlit_authenticator as stauth

st.set_page_config(page_title="Insights from Interviews")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "input_key" not in st.session_state:
    st.session_state.input_key = 0
# Load the .env variables
load_dotenv()

## Authentication ##

names = ['Mr Carlos', 'Imperium']
usernames = ['carlos', 'imperium']

# loading hashed passwords

file_path  = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "patient-interview", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main" )

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:

    # List all files in the 'sourcedata' directory
    source_data_dir = 'sourcedata'
    txt_files = [os.path.splitext(f)[0] for f in os.listdir(source_data_dir) if f.endswith('.txt')]

    # Add selectbox to the sidebar
    selected_file = st.sidebar.selectbox('Select the Person Name', txt_files)

    # Load selected file (append '.txt' to the selected file before opening)
    selected_file_path = os.path.join(source_data_dir, selected_file + '.txt')
    with open(selected_file_path, 'r') as file:
        text = file.read()

    document = Document(text)  # creating Document object
    documents = [document]

    # Create the index
    index = GPTVectorStoreIndex.from_documents(documents)

    # Create the query engine
    query_engine = index.as_query_engine()

    def handle_meta_question(question):
        if question.lower() == 'what was my first question?':
            for role, message in st.session_state.chat_history:
                if role == "User":
                    return message
        # Add more conditions here to handle other types of meta-questions
        return None

    # Streamlit UI

    st.sidebar.title(f"Welcome {name}!")
    authenticator.logout("Logout", "sidebar")

    st.title("Healthcare Encounters")

    user_question = st.text_input("Ask the person's insights here", key=st.session_state.input_key)

    if user_question:
        st.session_state.input_key += 1
        meta_answer = handle_meta_question(user_question)
        if meta_answer is not None:
            result = meta_answer
        else:
            result = query_engine.query(user_question).response
        st.session_state.chat_history.append(("User", user_question))
        st.session_state.chat_history.append(("Patient", result))

    for role, message in st.session_state.chat_history:
        if role == "User":
            st.markdown(f'**{role}**: {message}')
        else:
            st.markdown(f'**{role}**: {message}')
