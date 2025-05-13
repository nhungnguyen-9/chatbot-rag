import streamlit as st
from app.auth import CognitoAuth

def show_login_ui():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    auth = CognitoAuth()

    if st.button("Login", key="login_button"):
        try:
            access_token = auth.authenticate_user(username, password)
            user_info = auth.get_user_info(access_token)
            st.session_state["access_token"] = access_token
            st.session_state["user_id"] = user_info["Username"]
            st.success("Logged in successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {str(e)}")

    if st.button("Logout", key="logout_button") and "access_token" in st.session_state:
        del st.session_state["access_token"]
        del st.session_state["user_id"]
        st.success("Logged out successfully!")
        st.rerun()