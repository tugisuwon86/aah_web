import streamlit as st
#from streamlit_pandas_profiling import st_profile_report
import pandas as pd
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
        Page("pages/tutor_update.py", "Tutor Information Update"),
        
        Section(name="For Students Only", icon="💪"),    
        Page("pages/student_registration.py", "Student Registration"),
        Page("pages/tutor_signup.py", "Sign up for a session"),

        Section(name="Class Update", icon="💪"),    
        # Page("pages/cancel_session.py", "Student Registration"),
        Page("pages/complete_session.py", "Follow up"),
        Page("pages/summary.py", "Summary"),
        Page("pages/notification.py", "Notification"),
    ]
)
add_page_title() # By default this also adds indentation

# ---------------------------------------------------------------------------------------------------------
meta_col0, meta_col1, meta_col2 = st.columns(3)


subjects = {'academic': ['', 'English Conversation for International students', 'Elementary English & Language Arts', 
          'Middle School English & Language Arts', 'Elementary Math', 'Middle School Math', 'Pre-Algebra', 'Algebra I',
          'Algebra II', 'Geometry', 'Pre-Calculus', 'AP Calculus AB', 'AP Calculus BC', 'AP Physics', 'Beginner Spanish', 'Advanced Spanish', 
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

with st.form('tutor_registration_form'):
  email = st.text_input('Please type your teacher email')

  st.write('Choose as many as possible by selecting all -> leave it as blank if not!')
  st.write('**Please select English Conversation as one of your subjects!!**')
  math_subjects = st.multiselect('Which subject would you like to teach?', subjects['academic'])
  eng_subjects = st.multiselect('Which computer science subject would you like to teach?', subjects['Computer Science'])

      
  # convert array of subjects to string
  math_subjects = ','.join([xx for xx in math_subjects if xx != ''])
  eng_subjects = ','.join([xx for xx in eng_subjects if xx != ''])
    
  submitted = st.form_submit_button("Update Subjects")
  if submitted:
    # first check valid email
    #st.write(email, list(df_tutor['email'].values))
    if email not in list(df_tutor['email'].values):
      st.error('You are not registered', icon="🚨")
    else:
      complete1 = df_tutor[df_tutor['email'] == email].index[0]
      #st.write(complete1)
      wks_tutor.update_cell(complete1+2, 9, math_subjects)
      wks_tutor.update_cell(complete1+2, 10, eng_subjects)
      st.write("Updated")

  
