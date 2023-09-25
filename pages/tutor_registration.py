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
        Page("pages/summary.py", "Summary"),
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

with st.form('tutor_registration_form'):
  first_name = st.text_input('Your first name')
  last_name = st.text_input('Your last name')
  email = st.text_input('We are using Google Meet for tutoring services. Please type your Gmail')

  grade = st.selectbox('Your grade', [str(i)+'th' for i in range(8, 13)] + ['College Freshmen', 'College Sophomore', 'College Junior', 'College Senior'])
  country = st.text_input('Your country')
  referral = st.text_input('How did you hear about us?')

  school = st.text_input('Name of your school')
  telephone = st.text_input('Please provide valid number in case we need to reach you')
  
  #subjects = json.load(open('subjects.json'))

  st.write('Choose as many as possible by selecting all -> leave it as blank if not!')
  st.write('**Please select English Conversation as one of your subjects!!**')
  math_subjects = st.multiselect('Which subject would you like to teach?', subjects['academic'])
  eng_subjects = st.multiselect('Which computer science subject would you like to teach?', subjects['Computer Science'])

      
  # convert array of subjects to string
  math_subjects = ','.join([xx for xx in math_subjects if xx != ''])
  eng_subjects = ','.join([xx for xx in eng_subjects if xx != ''])

  st.divider()  # 👈 Draws a horizontal rule
  st.write("Please send an email to freetutoring@americanassimilationhelpline.org with photo ID to complete the registration!")
  st.write("Tutors need to provide 1) Student ID or 2) Driver license - if you don't have one, please send us your parent's driver license to complete your registration")

  st.markdown("**PLEASE READ BELOW BEFORE SUBMITTING YOUR APPLICATION**")
  para = '''
- We are using Google Meet for our online sessions (You need to have a Gmail account)
1) go to meet.Google.com
2) create an instant meeting
3) click on the i in a circle and copy the info
4) paste it in the email to your student

- Tutor can sign up for a session whenever you are available. There is no minimum or maximum number of sessions required for volunteers.

- Tutor must turn on your camera while you are in your session. 

- Tutor can find our teaching materials for your session from our website. 
For academic resources: https://www.americanassimilationhelpline.org/get_involved
For Computer Science resources: 
https://www.americanassimilationhelpline.org/coding
Your student might bring their own material they want to work on. 

- If you are tutoring English conversation, use or download Google Translate to translate English to your student's language - this allows for effective communication with your student. (for instance, Brazil's primary language is Portuguese)

- Take a screenshot during each session with you and your student and email us at Freetutoring@americanassimilationhelpline.org. We use this to confirm your session took place for your volunteer hours. Take the picture at the beginning of your session to ensure you don't forget.

- You need to download WhatsApp! We communicate through it. Every registered tutor will be added to one of our WhatsApp tutor group chats. 

- Record your volunteer hours to confirm them with us. 
  '''
  st.markdown(para)

  st.markdown('***COMMUNICATION***')
  para = '''
  Both tutor and student will receive an email (aahtutoringscheduler@gmail.com) from us with your student and tutor info. You won’t get an email from us if you don’t have your student. We match tutor and student by subjects and their availabilities. 
  '''
  st.markdown(para)
    
  sent = st.checkbox('Sent email')
    
  submitted = st.form_submit_button("Submit tutor registration form")
  if submitted and sent:
    # first check valid email
    if first_name.strip() == '' or last_name.strip() == '':
      st.error('please provide your full name', icon="🚨")
    elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
      st.error('please provide valid email address', icon="🚨")
    elif email.strip() in df_tutor['email'].values:
      st.error('you are already registered!', icon="🚨")
    else:
      df_tutor.loc[len(df_tutor.index)] = [first_name, last_name, email, grade, country, referral, school, telephone, math_subjects, eng_subjects, 'N']
      #st.dataframe(df_tutor)
      wks_tutor.update([df_tutor.columns.values.tolist()] + df_tutor.values.tolist())
      st.write("We received your registration! Please give us 24 hours to approve your registration!")

  


