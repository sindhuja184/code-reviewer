import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1/auth"
CODE_API_URL = "http://localhost:8000/api/v1/codereview"

def show_login_signup():
        
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

        st.markdown('--------')
        st.markdown('### Forgot Password')
        email_for_reset = st.text_input(
            'Enter your email to reset passwrd',
            key = 'reset_email'
        )
        if st.button("Send Password Reset Link"):
            if not email_for_reset:
                st.error("please enter your email")
            else:
                try:
                    response = requests.post(f"{API_URL}/password-reset-request", json={"email": email_for_reset})
                    if response.status_code == 200:
                        st.success("Check your email for password reset link")
                    else:
                        error_detail = response.json().get("detail", "Failed to send reset link")
                        st.error(f"Error: {error_detail}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")


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

# Code Review Routes Implementation

def get_my_reviews(access_token):
    headers = {"Authorization" : f"Bearer {access_token}"}
    try:
        response = requests.get(f"{CODE_API_URL}/my-reviews", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch reviews: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error cnnecting to backend: {e}")


def submit_code_review():
    st.header("Submit a New Code Review")

    title = st.text_input("Enter the title")
    code_snippet = st.text_input("Paste your code here")
    language = st.selectbox("Select Language", ["python", "javascript", "java", "c++"])

    if st.button("Submit for Review"):
        if not title or not code_snippet:
            st.error("Please fill ot all fields")
        else:
            headers = {
                "Authorization" : f"Bearer {st.session_state['access_token']}"
            }
            payload = {
                "title": title,
                "code_snippet" : code_snippet,
                "language": language
            }
            try:
                response = requests.post(f"{CODE_API_URL}/submit", json=payload, headers=headers)
                if response.status_code == 200:
                    st.success("Code Review submitted successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to submit review: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")

def update_review(review_id, title, code_snippet, language, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "title": title,
        "code_snippet": code_snippet,
        "language": language
    }
    try:
        response= requests.put(
            f"{CODE_API_URL}/{review_id}",
            headers=headers,
            json= payload
        )
        if response.status_code == 200:
            st.success("Review Updated Successfully!")
            st.rerun()
        else:
            st.sucess("Review updated successfully!!")
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

def delete_review(review_id, access_token):
    headers = {
        "Authorization" : f"Bearer {access_token}"
    }
    try:
        response = requests.delete(
            f"{CODE_API_URL}/{review_id}", headers= headers
        )
        if response.status_code == 204:
            st.success("Review delete successfully!!!")
            st.rerun()
        else:
            st.error(f"Failed to delete review: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")


### Account Verification
def show_account_verified():
    st.markdown("<h1 style='text-align: center;'>✅ Account Verified</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Your account has been successfully verified! You can now log in and start using Code Reviewer.</p>", unsafe_allow_html=True)

    if st.button("Go to Login Page"):
        st.session_state.clear()
        st.rerun()



def logout():
    st.session_state.clear()
    st.rerun()

def show_dashboard():
    st.title("📊 Code Review Dashboard")

    user = st.session_state.get('user', {})
    st.success(f"Welcome, **{user.get('username', 'User')}** 👋")

    st.sidebar.header("👤 Account")
    if st.sidebar.button("🚪 Logout"):
        logout()

    st.sidebar.markdown("---")
    st.sidebar.header("➕ Submit Code Review")

    with st.sidebar.form("submit_review_form"):
        title = st.text_input("Title")
        code_snippet = st.text_area("Paste your code here")
        language = st.selectbox("Select Language", ["python", "javascript", "java", "c++", "other"])
        submit = st.form_submit_button("Submit")

        if submit:
            if not title or not code_snippet:
                st.sidebar.error("Please fill all fields.")
            else:
                headers = {
                    "Authorization": f"Bearer {st.session_state['access_token']}"
                }
                payload = {
                    "title": title,
                    "code_snippet": code_snippet,
                    "language": language
                }

                try:
                    response = requests.post(f"{CODE_API_URL}/submit", json=payload, headers=headers)
                    if response.status_code == 200:
                        st.sidebar.success("✅ Review submitted!")
                        st.rerun()
                    else:
                        st.sidebar.error(f"Failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")

    st.markdown("## Your Code Reviews")

    reviews = get_my_reviews(st.session_state['access_token'])

    if reviews:
        for review in reviews:
            with st.expander(f"{review['title']}"):
                st.code(review['code_snippet'], language="python")
                st.markdown(f"**Review:** {review.get('review', 'No review generated yet.')}")


                if st.toggle("Edit this Review", key = f"edit_toggle_{review['uid']}"):
                    new_title = st.text_input("Title", value=review['title'], key=f"title_{review['uid']}")
                    new_code = st.text_area("Code Snippet", value=review['code_snippet'], height=200, key=f"code_{review['uid']}")
                    new_lang = st.selectbox("Language", ["python", "javascript", "c++", "java"], key=f"lang_{review['uid']}")

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        if st.button("Update Review", key = f"update_{review['uid']}"):
                            update_review(
                                review_id=review['uid'],
                                title=new_title,
                                code_snippet=new_code,
                                language=new_lang,
                                access_token=st.session_state['access_token']
                            )
                    
                    with col2:
                        if st.button("Delete Review", key=f"delete_{review['uid']}"):
                            confirm = st.radio("Are you sure?", ["No", "Yes"], key=f"confirm_delete_{review['uid']}")
                            if confirm == "Yes":
                                delete_review(
                                    review['uid'],
                                    st.session_state['access_token']
                                )


    else:
        st.info("You have no code reviews yet.")

def main():
    st.set_page_config(page_title="Code Reviewer")

    query_params = st.query_params

    if "verified" in query_params:
        show_account_verified()
    elif 'access_token' in st.session_state:
        show_dashboard()
    else:
        show_login_signup()

if __name__ == "__main__":
    main()