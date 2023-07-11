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

with st.form('tutor_registration_form'):
  first_name = st.text_input('Your first name')
  last_name = st.text_input('Your last name')
  email = st.text_input('Please type your email - must provide valid email; otherwise, the registration will be rejected')

  grade = st.slider('Your grade', 5, 12, 5)
  country = st.text_input('Your country')
  referral = st.text_input('How did you hear about us?')

  math_subjects = st.multiselect('Which math subject would you like to teach?' ['Elementary Math', 'Middle School Math', 'Pre-Algebra', 'Algebra', 'Pre-Calculus'])
  eng_subjects = st.multiselect('Which english subject would you like to teach?' ['Elementary English', 'Middle School English'])

  submitted = st.form_submit_button("Submit tutor registration form")
  if submitted:
    # first check valid email
    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
      st.error('please provide valid email address', icon="🚨")
    elif email.strip() in wks_tutor['email']:
      st.error('you are already registered!', icon="🚨")
    else:
      wks_tutor.append_row([first_name, last_name, email, grade, country, referral, math_subjects, eng_subjects, 'N'])
      st.write("We received your registration! Please give us 24 hours to approve your registration!")

  


