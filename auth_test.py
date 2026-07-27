import streamlit as st

st.set_page_config(
    page_title="Authentication Test"
)

if not st.user.is_logged_in:
    st.title("Authentication Test")

    st.write(
        "Please sign in to continue."
    )

    if st.button(
        "Continue with Google",
        use_container_width=True
    ):
        st.login()

    st.stop()


st.title("Login Successful")

st.write(
    f"Welcome, {st.user.name}"
)

st.write(
    f"Email: {st.user.email}"
)

st.write(
    f"User ID: {st.user.sub}"
)

if st.button("Sign Out"):
    st.logout()