import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ['Mr Carlos', 'Mr Pablo', 'Imperium']
usernames = ['carlos', 'pablo', 'imperium']
passwords = ['abc321', 'def654', 'ghi987']

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"

with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)