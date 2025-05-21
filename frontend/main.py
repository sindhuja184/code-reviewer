import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1/auth"

st.set_page_config(page_title="Login / Signup", page_icon="🔐")


st.title("Welcome to Code Reviewer")
st.write("Please login or signup to continue")


auth_mode = st.radio(
    "Select Action",
    ["Login", "Signup"]
)

if auth_mode == "Login":
    st.subheader("Login to your account")

    username = st.text_input("Username")
    password = st.text_input("Passwrd", type= "password")

    if st.button("Login"):
        if not username or not password:
            st.error("Please enter username and password")
        else:
            payload = {
                "username": username,
                "password": password
            }

            try:
                response = requests.post(f"{API_URL}/login", json= payload)
                if response.status_code == 200:
                    data = response.json()
                    st.success("Login Successful!!")
                    st.session_state['access_token'] = data['access_token']
                    st.session_state['refresh_token'] = data['refresh_token']
                    st.session_state['user'] = data['user']
                else:
                    error_detail = response.json().get('detail', 'Login Failed')
                    st.error(f"Error: {error_detail}")
            except Exception as e:
                st.error(f"Error connecting to backend")

elif auth_mode == "Signup":
    st.subheader("Create a new account")
    firstname = st.text_input("First Name")
    lastname = st.text_input("Last Name")
    new_username = st.text_input("Username", key="signup_username")
    email = st.text_input("Email")
    new_password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

    if st.button("Signup"):
        if not new_username or not email or not new_password or not confirm_password or not firstname or not lastname: 
            st.error("All fields are required")
        elif new_password != confirm_password:
            st.error("Passwords do not match")
        else:
            # Call backend signup API
            payload = {
                "firstname": firstname, 
                "lastname": lastname,
                "username": new_username,
                "email": email,
                "password": new_password
            }
            try:
                response = requests.post(f"{API_URL}/signup", json=payload)
                if response.status_code == 201:
                    st.success("Signup successful! Check your email to verify your account.")
                else:
                    error_detail = response.json().get('detail', 'Signup failed')
                    st.error(f"Error: {error_detail}")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")

if 'access_token' in st.session_state:
    user = st.session_state.get('user', {})

    st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
    st.sidebar.image("https://avatars.githubusercontent.com/u/9919?s=280&v=4", width=100)  # Example avatar

    st.sidebar.markdown(f"### 👤 {user.get('firstname', '')} {user.get('lastname', '')}")
    st.sidebar.markdown(f"**Username:** {user.get('username', '')}")
    st.sidebar.markdown(f"**Email:** {user.get('email', '')}")
    st.sidebar.divider()

    tab = st.sidebar.radio("🧭 Navigation", ["🏠 Dashboard", "👤 Profile", "🧠 Code Review", "⚙️ Settings"])

    st.markdown(f"## 👋 Welcome, {user.get('firstname', '')}!")

    if tab == "🏠 Dashboard":
        st.subheader("📊 Dashboard Overview")

        col1, col2, col3 = st.columns(3)
        col1.metric("📝 Reviews Done", "12", "+3")
        col2.metric("⏳ Pending Requests", "4", "-1")
        col3.metric("⚡ Avg Response Time", "1.5s", "-0.3s")

        st.markdown("### 🔄 Recent Activity")
        st.info("Coming Soon: Display of user actions, reviews, uploads...")

    elif tab == "👤 Profile":
        st.subheader("👤 Profile Information")
        st.json(user)

    elif tab == "🧠 Code Review":
        st.subheader("🧠 AI Code Review Tool")
        st.markdown("🚧 *Feature in development*")

    elif tab == "⚙️ Settings":
        st.subheader("⚙️ App Settings")
        st.markdown("Coming soon: Notification preferences, themes, etc.")

    # Logout button
    st.sidebar.divider()
    if st.sidebar.button("🔓 Logout"):
        st.session_state.clear()
        st.rerun()