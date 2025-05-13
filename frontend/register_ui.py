import streamlit as st
import boto3
import os

COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_REGION = os.getenv("COGNITO_REGION")

def show_register_ui():
    st.title("📝 Register")

    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if not email or not username or not password:
            st.warning("Please fill all fields.")
            return

        client = boto3.client("cognito-idp", region_name=COGNITO_REGION)
        try:
            response = client.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    },
                ]
            )
            st.success("✅ Registration successful. Check your email for confirmation code.")
            st.session_state["pending_confirmation"] = username  # Save username for confirm step
        except client.exceptions.UsernameExistsException:
            st.error("🚫 Username already exists.")
        except Exception as e:
            st.error(f"Registration error: {str(e)}")

    # Xác nhận mã nếu có người đăng ký
    if "pending_confirmation" in st.session_state:
        st.subheader("📩 Confirm your Email")
        confirm_code = st.text_input("Confirmation Code")
        if st.button("Confirm"):
            try:
                client = boto3.client("cognito-idp", region_name=COGNITO_REGION)
                client.confirm_sign_up(
                    ClientId=COGNITO_CLIENT_ID,
                    Username=st.session_state["pending_confirmation"],
                    ConfirmationCode=confirm_code,
                )
                st.success("🎉 Email confirmed. You can now login.")
                del st.session_state["pending_confirmation"]
            except client.exceptions.CodeMismatchException:
                st.error("❌ Invalid confirmation code.")
            except Exception as e:
                st.error(f"Confirmation error: {str(e)}")
