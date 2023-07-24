import pickle
from pathlib import Path

import os
from dotenv import load_dotenv
import streamlit as st
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
import streamlit_authenticator as stauth

st.set_page_config(page_title="Insights from Interviews")
# Load the .env variables
load_dotenv()

## Authentication ##

names = ['Mr Carlos', 'Mr Pablo']
usernames = ['carlos', 'pablo']

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
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    
    # Load documents
    documents = SimpleDirectoryReader('sourcedata').load_data()

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




    st.title("Experiences by Patient 'A' ")

    user_question = st.text_input("Ask the Patient's insights here", key=st.session_state.input_key)

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
