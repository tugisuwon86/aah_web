import streamlit as st
#from streamlit_pandas_profiling import st_profile_report
import pandas as pd
import pandas_profiling
import re
import json

st.markdown("""
    <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 250px;
        }
    </style>
    """, unsafe_allow_html=True)


# st.title('AAH Tutor Registration')

from st_pages import Page, Section, show_pages, add_page_title
show_pages(
    [
        Page("main.py", "Home", "🏠"),
        Section(name="For Tutors Only", icon="🎈️"),
        Page("pages/tutor_registration.py", "Tutor Registration"),
        Page("pages/tutor_availability.py", "Tutor Availability Update"),
        
        Section(name="For Students Only", icon="💪"),    
        Page("pages/student_registration.py", "Student Registration"),
        Page("pages/tutor_signup.py", "Sign up for a session"),

        Section(name="Class Update", icon="💪"),    
        # Page("pages/cancel_session.py", "Student Registration"),
        Page("pages/complete_session.py", "Follow up"),
        Page("pages/summary.py", "Summary - Admin Only"),
        Page("pages/notification.py", "Notification - Admin Only"), 
    ]
)
add_page_title() # By default this also adds indentation

# ---------------------------------------------------------------------------------------------------------
meta_col0, meta_col1, meta_col2 = st.columns(3)


subjects = {'academic': ['', 'English Conversation for International students', 'Elementary English & Language Arts', 
          'Middle School English & Language Arts', 'Elementary Math', 'Middle School Math', 'Pre-Algebra', 'Algebra I',
          'Algebra II', 'Geometry', 'Pre-Calculus', 'AP Calculus AB', 'AP Calculus BC', 'Beginner Spanish', 'Advanced Spanish', 
          'SAT', 'ACT', 'Learning Lab - (Do not select any subject we only offer in person section)'], 
  'Computer Science': ['', 'Scratch', 'HTML/CSS', 'General Programming Concepts', 'Intro to Python', 'Intermediate/Advanced Python', 
                      'Intro to JAVA', 'Intermediate/Advanced JAVA']
}
# ---------------------------------------------------------------------------------------------------------
# Read data from google sheets to initiate
import gspread

credentials = st.secrets['gcp_service_account']
sa = gspread.service_account_from_dict(credentials)
sh = sa.open("AAh schedules")

wks_tutor = sh.worksheet("Tutors_Registration")

# read google sheets as dataframe
df_tutor = pd.DataFrame(wks_tutor.get_all_records())
# st.dataframe(df_tutor)


name = st.text_input('Enter admin username')
password = st.text_input('Enter password')

if name == 'Admin' and password == 'aahAdmin123':
  
  with st.form('tutor_registration_form'):
    
      
    submitted = st.form_submit_button("Send email to approved tutors")
    if submitted:
      
        df_tutor.loc[len(df_tutor.index)] = [first_name, last_name, email, grade, country, referral, school, telephone, math_subjects, eng_subjects, 'N']
        #st.dataframe(df_tutor)
        wks_tutor.update([df_tutor.columns.values.tolist()] + df_tutor.values.tolist())
        st.write("We received your registration! Please give us 24 hours to approve your registration!")
else:
  st.error('Wrong username and password')
    
