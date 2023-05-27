import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to AAH Tutor Scheduler Website! 👋")

st.sidebar.success("Select the menu")

st.markdown(
    """
    
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out our main website
    - Please sign up from the main website (both tutors and students) before visiting this site
    - You won't be able to sign up for tutor unless you are fully registered!
    ### See more complex demos
    - Tutors: Please update your schedule weekly to participate
    - Students: It is your responsibility to show up during signed session
"""
)