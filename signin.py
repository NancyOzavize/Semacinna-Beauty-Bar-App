import streamlit as st

def signin():
    st.title("Welcome Back 💖")

    with st.form("signin_form"):
        name = st.text_input("User Name")
        submitted = st.form_submit_button("Sign In")

        if submitted:
            st.success("Login successful. Redirecting...")
            st.session_state.page = "chat"
            st.session_state.name = name  # Or pull name from database
