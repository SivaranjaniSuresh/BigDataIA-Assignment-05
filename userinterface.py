import streamlit as st

from navigation.emergency_contacts import emergency
from navigation.forex import forex
from navigation.manual import manual
from navigation.translate import translate
from navigation.youtube import youtube

# Define the Streamlit pages
pages = {
    "YouTube": youtube,
    "Manual": manual,
    "Translate": translate,
    "Forex": forex,
    "Emergency Contacts": emergency,
}


def main():
    st.sidebar.title("Navigation")
    if "current_page" not in st.session_state:
        st.session_state.current_page = ""
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    # Clear session state if the current page is different from the previous page
    if selection != st.session_state.current_page:
        st.session_state.clear()
        st.session_state.current_page = selection

    page = pages[selection]
    page()


if __name__ == "__main__":
    main()
