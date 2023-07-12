import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

add_page_title() # By default this also adds indentation

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("home.py", "Home", "🏠"),
        Section(name="For Tutors Only", icon="🎈️"),
        Page("pages/tutor_registration.py", "Tutor Registration"),
        Page("pages/tutor_availability.py", "Tutor Availability Update"),
        Section(name="For Students Only", icon="💪"),    
        Page("pages/student_registration.py", "Student Registration"),
        Page("pages/tutor_signup.py", "Tutor Sign Up"),
    ]
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
