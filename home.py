import streamlit as st

def home():
    st.set_page_config(page_title="Semacinna Beauty Bar 💄", layout="centered")

    st.image("lip_logo.png", width=300)
    st.title("Welcome to Semacinna Beauty Bar 💋")
    st.markdown("**Your personal makeup shopper is here to serve you!**")

    st.write("")  # spacer

    col1, col2 = st.columns(2)

    with col1:
        if st.button("First-time Customer"):
            st.session_state.page = "signup"

    with col2:
        if st.button("Returning Customer"):
            st.session_state.page = "signin"
