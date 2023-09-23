import streamlit as st
#from streamlit_pandas_profiling import st_profile_report
import pandas as pd
import pandas_profiling
from datetime import datetime
import datetime as dt
import pytz
import json

st.set_page_config(page_title="Tutor Sign up Form", page_icon="📈")

from st_pages import Page, Section, show_pages, add_page_title
show_pages(
    [
        Page("main.py", "Home", "🏠"),
        Section(name="For Tutors Only", icon="🎈️"),
        Page("pages/tutor_registration.py", "Tutor Registration"),
        Page("pages/tutor_availability.py", "Tutor Availability Update"),
        
        Section(name="For Students Only", icon="💪"),    
        Page("pages/student_registration.py", "Student Registration"),
        Page("pages/tutor_signup.py", "Sing up for a session"),

        Section(name="Class Update", icon="💪"),    
        # Page("pages/cancel_session.py", "Student Registration"),
        Page("pages/complete_session.py", "Follow up"),
        Page("pages/summary.py", "Summary"),
    ]
)
add_page_title() # By default this also adds indentation

meta_col0, meta_col1 = st.columns(2) #, meta_col2, meta_col3 = st.columns(4)
# ---------------------------------------------------------------------------------------------------------
                
# ---------------------------------------------------------------------------------------------------------


# Read data from google sheets to initiate
import gspread

credentials = st.secrets['gcp_service_account']
sa = gspread.service_account_from_dict(credentials)
sh = sa.open("AAh schedules")

wks_schedule = sh.worksheet("Tutor Student Matching")
wks_tutor = sh.worksheet("Tutors_Registration")
wks_student = sh.worksheet('Students_Registration')
wks_absense = sh.worksheet("Tutors Absense")
wks_tutor_schedule = sh.worksheet("Tutor Weekly Schedule")

# read google sheets as dataframe
df = pd.DataFrame(wks_schedule.get_all_records())
df_tutor = pd.DataFrame(wks_tutor.get_all_records())
# filter by completed registration
df_tutor = df_tutor[df_tutor['complete'] == 'Y']

df_student = pd.DataFrame(wks_student.get_all_records())
df_schedule = pd.DataFrame(wks_tutor_schedule.get_all_records())

absent = {}
for row in df_schedule.values:
    absent[row[0]] = [row[1], row[2]]
#print('absent', absent)

tab1, tab2 = st.tabs(['Teacher', 'Student'])


with tab1:
    st.header('Teacher Follow up')
    email1 = st.text_input('Please type your teacher email')
    df_ = df[(df['Email'] == email1) & (df['Tutor Confirm'] == 'N')]
    st.table(df_[['Name', 'Subject', 'Schedule', 'Date']])

    options = df_.index
    complete = st.selectbox('Which session did you complete?', options)
    with st.form('teacher_form'):
        submitted = st.form_submit_button('Submit')
        if submitted:
            wks_schedule.update_cell(complete+1, 7, 'Y')
            st.write('Updated!')
with tab2:
    st.header('Student Follow up')
    email2 = st.text_input('Please type your student email')
    df_ = df[(df['Student Email'] == email2) & (df['Student Confirm'] == 'N')]
    st.table(df_[['Name', 'Subject', 'Schedule', 'Date']])

    options = df_.index
    complete = st.selectbox('Which session did you complete?', options)
    with st.form('student_form'):
        submitted = st.form_submit_button('Submit')
        if submitted:
            wks_schedule.update_cell(complete+1, 8, 'Y')
            st.write('Updated!')
