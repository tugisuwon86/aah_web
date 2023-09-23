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

def mailing(tutor, subject, email_tutor, tutor_time, tutor_date, email_student):
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(f"""
    Hello, 

    You have signed up for the following tutor session:
    Tutor: {tutor}
    Subject: {subject}
    Datetime: {tutor_date} {tutor_time}

    If you need to cancel/reschedule, please send email to freetutoring@americanassimilationhelpline.org. Your tutor will reach out with google meet link prior to the sessions. Thanks.
    
    """[1:])
    msg['Subject'] = 'AAH Tutoring Schedule Confirmation'
    connection = smtplib.SMTP('smtp.gmail.com', 587)
    connection.starttls()
    connection.login('aahtutoringscheduler@gmail.com','qdqrhbtswkkemzlw')#'lnafzpcllnnpwtmk') #'@RQu&S56pAS1')
    connection.sendmail('aahtutoringscheduler@gmail.com', email_student, msg.as_string())
    connection.quit()

    msg = MIMEText(f"""
    Hello, 

    Student has signed up for the following tutor session:
    Subject: {subject}
    Datetime: {tutor_date} {tutor_time} EDT

    -We are using Google Meet for our online sessions (You need to have a Gmail account)
    1) go to meet.Google.com
    2) create an instant meeting
    3) click on the i in a circle and copy the info
    4) paste it in the email to your student

    -Tutor must turn on your camera while you are in your session. 

    -Tutor can find our teaching materials for your session from our website. 
    For academic resources: https://www.americanassimilationhelpline.org/get_involved
    For Computer Science resources: 
    https://www.americanassimilationhelpline.org/coding
    Your student might bring their own material they want to work on. 
    
    -If you are tutoring English conversation, use or download Google Translate to translate English to your student's language - this allows for effective communication with your student. (for instance, Brazil's primary language is Portuguese)
    
    -Take a screenshot during each session with you and your student and email us at Freetutoring@americanassimilationhelpline.org. We use this to confirm your session took place for your volunteer hours. Take the picture at the beginning of your session to ensure you don't forget.
    
    -You need to download WhatsApp! We communicate through it. Every registered tutor will be added to one of our WhatsApp tutor group chats. 
    
    -Record your volunteer hours to confirm them with us. 

    If you are not available at this time, please send email to freetutoring@americanassimilationhelpline.org. Please reach out to {email_student} with google meet link before the session. Thanks.
    
    """[1:])
    msg['Subject'] = 'AAH Tutoring Schedule Confirmation'
    connection = smtplib.SMTP('smtp.gmail.com', 587)
    connection.starttls()
    connection.login('aahtutoringscheduler@gmail.com','qdqrhbtswkkemzlw')#'lnafzpcllnnpwtmk') #'@RQu&S56pAS1')
    connection.sendmail('aahtutoringscheduler@gmail.com', email_tutor, msg.as_string())
    connection.quit()

    # # Import the email modules we'll need
    # from email.message import EmailMessage
    # msg = EmailMessage()
    
    # msg['Subject'] = f'AAH Tutoring Schedule Confirmation'
    # msg['From'] = 'AAH'
    # msg['To'] = email_tutor
    # msg.preamble = f"""
    # Hello, 

    # You have signed up for the following tutor session:
    # Tutor: {tutor}
    # Subject: {subject}
    # Datetime: {tutor_date} {tutor_time} EDT

    # If you need to cancel/reschedule, please send email to freetutoring@americanassimilationhelpline.org. Your tutor will reach out with google meet link prior to the sessions. Thanks.
    
    # """[1:]
    
    # # Send the message via our own SMTP server, but don't include the
    # # envelope header.
    # with smtplib.SMTP('localhost') as s:
    #     s.send_message(msg)

    # msg = EmailMessage()
    # msg['Subject'] = f'AAH Tutoring Schedule Confirmation'
    # msg['From'] = 'AAH'
    # msg['To'] = email_student
    # msg.preamble = f"""
    # Hello, 

    # Student has signed up for the following tutor session:
    # Subject: {subject}
    # Datetime: {tutor_date}

    # If you are not available at this time, please send email to freetutoring@americanassimilationhelpline.org. Please reach out to {email} with google meet link before the session. Thanks.
    
    # """[1:]
    # with smtplib.SMTP('localhost') as s:
    #     s.send_message(msg)

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
email = st.text_input('Please type your email (must match with email we have in our system')

with tab1:
    st.header('Teacher Follow up')
    df_ = df_schedule[(df_schedule['Email'] == email) & (df_schedule['Tutor Confirm'] == 'N')]
    st.table(df_)

    options = [f'Date {x[4]}, Time {x[3]}, Subject {x[1]} for x in df_.values']
    complete = st.selectbox('Which session did you complete?', options)
    
with tab2:
    st.header('Student Follow up')
