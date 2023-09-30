import streamlit as st
#from streamlit_pandas_profiling import st_profile_report
import pandas as pd
import pandas_profiling
import re

st.markdown("""
    <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 250px;
        }
    </style>
    """, unsafe_allow_html=True)


# st.title('AAH Student Registration')
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
    ]
)
add_page_title() # By default this also adds indentation

# ---------------------------------------------------------------------------------------------------------
meta_col0, meta_col1, meta_col2 = st.columns(3)

# ---------------------------------------------------------------------------------------------------------
# Read data from google sheets to initiate
import gspread

credentials = st.secrets['gcp_service_account']
sa = gspread.service_account_from_dict(credentials)
sh = sa.open("AAh schedules")

wks_student = sh.worksheet("Students_Registration")

# read google sheets as dataframe
df_student = pd.DataFrame(wks_student.get_all_records())
# st.dataframe(df_student)

with st.form('tutor_registration_form'):
  first_name = st.text_input('Your first name')
  last_name = st.text_input('Your last name')
  email = st.text_input('We are using Google Meet for tutoring services. Please type your Gmail')
  num = st.text_input('Please provide valid number in case we need to reach you')  

  grade = st.selectbox('Your grade', ['Kinder', '1st', '2nd', '3rd'] + [str(i)+'th' for i in range(4, 13)])
  country = st.text_input('Your country')
  #referral = st.text_input('How did you hear about us?')

  school = st.text_input('Your school')

  st.divider()  # 👈 Draws a horizontal rule
  st.write("Please send an email to freetutoring@americanassimilationhelpline.org with photo ID to complete the registration!")
  st.write("Students need to provide 1) Student ID or 2) Driver license - if you don't have one, please send us your parent's driver license to complete your registration")
  sent = st.checkbox('Sent email')

  st.markdown('***COMMUNICATION***')
  para = '''
  Both tutor and student will receive an email (aahtutoringscheduler@gmail.com) from us with your student and tutor info. You won’t get an email from us if you don’t have your student. We match tutor and student by subjects and their availabilities. 
  '''
  st.markdown(para)
    
  submitted = st.form_submit_button("Submit tutor registration form")
  if submitted and sent:
    # first check valid email
    if first_name.strip() == '' or last_name.strip() == '':
      st.error('please provide your full name', icon="🚨")
    elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
      st.error('please provide valid email address', icon="🚨")
    elif email.strip() in df_student['email'].values:
      st.error('you are already registered!', icon="🚨")
    else:
      df_student.loc[len(df_student.index)] = [first_name, last_name, email, grade, country, num, school, 'N', 'N']
      #st.dataframe(df_student)
      wks_student.update([df_student.columns.values.tolist()] + df_student.values.tolist())
      st.write("We received your registration! Please give us 24 hours to approve your registration!")

  

