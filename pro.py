import streamlit as st
import home
import signin
import signup
import chat
import checkout

# Set default page
if "page" not in st.session_state:
    st.session_state.page = "home"



if st.session_state.page == "home":
    home.home()
elif st.session_state.page == "signup":
    signup.signup()
elif st.session_state.page == "signin":
    signin.signin()
elif st.session_state.page == "chat":
    chat.chat()
elif st.session_state.page == "checkout":
    checkout.checkout()

