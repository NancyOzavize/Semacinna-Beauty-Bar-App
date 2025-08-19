import streamlit as st

def signup():
    st.title("Sign Up 💅")

    with st.form("signup_form"):
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        shade = st.text_input("Favorite Product")
        submitted = st.form_submit_button("Sign Up & Start Chatting")

        if submitted:
            st.success(f"Welcome, {name}! Redirecting to chat...")
            st.session_state.page = "chat"
            st.session_state.name = name
