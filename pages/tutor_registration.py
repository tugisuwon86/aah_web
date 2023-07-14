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


st.title('AAH Tutor Registration')

from st_pages import Page, Section, show_pages, add_page_title
show_pages(
    [
        Page("main.py", "Home", "🏠"),
        Section(name="For Tutors Only", icon="🎈️"),
        Page("pages/tutor_registration.py", "Tutor Registration"),
        Page("pages/tutor_availability.py", "Tutor Availability Update"),
        
        Section(name="For Students Only", icon="💪"),    
        Page("pages/student_registration.py", "Student Registration"),
        Page("pages/tutor_signup.py", "Tutor Sign Up"),
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

wks_tutor = sh.worksheet("Tutors_Registration")

# read google sheets as dataframe
df_tutor = pd.DataFrame(wks_tutor.get_all_records())
st.dataframe(df_tutor)

with st.form('tutor_registration_form'):
  first_name = st.text_input('Your first name')
  last_name = st.text_input('Your last name')
  email = st.text_input('Please type your email - must provide valid email; otherwise, the registration will be rejected')

  grade = st.selectbox('Your grade', [str(i)+'th' for i in range(5, 13)] + ['freshmen', 'sophomore', 'junior', 'senior'])
  country = st.text_input('Your country')
  referral = st.text_input('How did you hear about us?')

  school = st.text_input('Name of your school')
  telephone = st.text_input('Please provide valid number in case we need to reach you')
  

  math_subjects = st.multiselect('Which math subject would you like to teach?', ['Elementary Math', 'Middle School Math', 'Pre-Algebra', 'Algebra', 'Pre-Calculus'])
  eng_subjects = st.multiselect('Which english subject would you like to teach?', ['Elementary English', 'Middle School English'])

      
  # convert array of subjects to string
  math_subjects = ','.join(math_subjects)
  eng_subjects = ','.join(eng_subjects)

  submitted = st.form_submit_button("Submit tutor registration form")
  if submitted:
    # first check valid email
    if first_name.strip() == '' or last_name.strip() == '':
      st.error('please provide your full name', icon="🚨")
    elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
      st.error('please provide valid email address', icon="🚨")
    elif email.strip() in df_tutor['email'].values:
      st.error('you are already registered!', icon="🚨")
    else:
      df_tutor.loc[len(df_tutor.index)] = [first_name, last_name, email, grade, country, referral, school, telephone, math_subjects, eng_subjects, 'N']
      st.dataframe(df_tutor)
      wks_tutor.update([df_tutor.columns.values.tolist()] + df_tutor.values.tolist())
      st.write("We received your registration! Please give us 24 hours to approve your registration!")

  


