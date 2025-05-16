import streamlit as st
from app.auth import CognitoAuth

def show_login_ui():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    auth = CognitoAuth()

    if st.button("Login", key="login_button"):
        try:
            result = auth.authenticate_user(username, password)
            st.session_state["access_token"] = result["id_token"] 
            st.session_state["credentials"] = result["credentials"]  # Lưu credentials
            st.session_state["user_id"] = username  # Sử dụng username làm user_id
            st.success("Logged in successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {str(e)}")

    if st.button("Logout", key="logout_button") and "access_token" in st.session_state:
        del st.session_state["access_token"]
        del st.session_state["credentials"]
        del st.session_state["user_id"]
        st.success("Logged out successfully!")
        st.rerun()