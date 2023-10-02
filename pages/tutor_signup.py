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
        Page("pages/tutor_signup.py", "Sign up for a session"),

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
df_abs = pd.DataFrame(wks_absense.get_all_records())
df_schedule = pd.DataFrame(wks_tutor_schedule.get_all_records())

absent = {}
for row in df_schedule.values:
    absent[row[0]] = [row[1], row[2]]
#print('absent', absent)

email = st.text_input('Please type your email (must match with email we have in our system')
st.write('Your email address is: ', email)
st.write('Make sure your email address if accurate before proceeding; otherwise, you will not be able to sign up for tutor')

st.write('Your status summary---------')
# make sure the student is in our system
NOW = (dt.datetime.utcnow()).replace(hour=0, minute=0, second=0, microsecond=0)
check_ = df_student[(df_student['email'] == email) & (df_student['complete'] == 'Y')]
number_of_booking = df[(df['Student Email'] == email) & (df['Date'] >= str(NOW.date()))]

current_booking = number_of_booking[['Name', 'Subject', 'Schedule']]
current_booking.columns = ['Tutor Name', 'Subject', 'Schedule']
st.table(current_booking)

if check_.shape[0] == 0:
    st.error('Your email address is not found in our system. Please register from the main website first', icon="🚨")
elif number_of_booking.shape[0] >= 20:
    st.error('You booked more than the number of weekly limit')

#subject_options = sorted(tuple(set(df['Subject'].values)))

# subjects_ = json.load(open('subjects.json'))
subjects_ = {'academic': ['English Conversation for International students', 'Elementary English & Language Arts', 
          'Middle School English & Language Arts', 'Elementary Math', 'Middle School Math', 'Pre-Algebra', 'Algebra I',
          'Algebra II', 'Geometry', 'Pre-Calculus', 'AP Calculus AB', 'AP Calculus BC', 'Beginner Spanish', 'Advanced Spanish', 
          'SAT', 'ACT', 'Learning Lab - (Do not select any subject we only offer in person section)'], 
  'Computer Science': ['Scratch', 'HTML/CSS', 'General Programming Concepts', 'Intro to Python', 'Intermediate/Advanced Python', 
                      'Intro to JAVA', 'Intermediate/Advanced JAVA']
}
subject = meta_col0.selectbox('Subject', subjects_['academic'] + subjects_['Computer Science'])
#subject_2 = meta_col0.selectbox('Computer Science Subject', subjects_['Computer Science'])

# NOW = (dt.datetime.utcnow()).replace(hour=0, minute=0, second=0, microsecond=0)
# tutor_date = meta_col1.date_input("Tutor Date", NOW, min_value=NOW, max_value=(NOW+dt.timedelta(days=14)).date())
# # convert tutor_date to day of week
# tutor_dow = tutor_date.weekday()
dow_mapping = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
dow = meta_col1.selectbox('Day of Week', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
while True:
    if dow_mapping[NOW.weekday()] == dow:
        break
    NOW += dt.timedelta(days=1)
tutor_date = NOW.date()
st.write(f'**The following tutors/time are available for {dow}: {tutor_date}**')
st.write('Please choose different day of week if you cannot find the spot you want')
#st.write(tutor_date, str(tutor_date), tutor_dow)

# tutor_time = meta_col2.selectbox('Time', [str(i)+' PM -'+str(i+1) + ' PM'for i in range(2, 10)])

tutor_option_1 = df_tutor.loc[((df_tutor['math_subjects'].str.contains(subject)) | (df_tutor['english_subjects'].str.contains(subject)))]
#st.table(tutor_option_1)
tutor_option_2 = df_schedule.loc[(df_schedule['Schedule'].str.contains(dow))] #== dow_mapping[tutor_dow] + " : " + tutor_time)]

options = [x[0] + ' || ' + x[2] for x in tutor_option_2.values]
session = st.selectbox("Choose the session - everything is in EDT timezone", options)
print('---------------------------')
st.table(tutor_option_2)
name_mapping, email_mapping = {}, {}
for row in tutor_option_2[['Email', 'Name']].values:
    name_mapping[row[0]] = row[1]
    email_mapping[row[1]] = row[0]
tutor_option = list(sorted(set(tutor_option_1.email.values) & set(tutor_option_2.Email.values)))
#print('tutor option', tutor_option)

# make sure tutor is available by comparing it with tutor's absent schedule
# tutor_option_ = []
# for t in tutor_option:
#     if t in absent:
#         if absent[t][0] <= str(tutor_date) <= absent[t][1]:
#             continue
#     tutor_option_ += [t]
# tutor_option = [name_mapping[x] for x in tutor_option_]
# tutor = meta_col3.selectbox('Tutor', tutor_option)
#st.write('tutor: ' + tutor)
tutor, schedule = session.split(' || ')
_, tutor_time = schedule.split(' : ')
if tutor in email_mapping:
    email_ = email_mapping[tutor]

    # ---------------------------------------------------------------------------------------------------------
    #st.write('date: ', str(tutor_date))
    taken = df.loc[(df['Email'] == email_) & (df['Date'] == str(tutor_date))] # already taken
    taken_hours = taken.Schedule.values
    available = tutor_option_2 .loc[(tutor_option_2 ['Email'] == email_) & (~tutor_option_2 ['Schedule'].isin(taken_hours))] # filtered by day of week and email
    
    #option = st.selectbox('Please choose the time slot you want to schedule: ', sorted(available['Schedule'].values))
    #st.write('You selected: ' + option)
    
    with st.form('save_form'):
        save_submitted = st.form_submit_button('Please click to book the slot')
    
    # make sure the student is in our system
    check_ = df_student[(df_student['email'] == email) & (df_student['complete'] == 'Y')]
    #print(check_, tutor, option)
    #print(df.head())

    if save_submitted:
        if number_of_booking.shape[0] >= 2:
            st.error('You booked more than the number of weekly limit', icon="🚨")
        elif check_.shape[0] > 0:
            # index = df.index[(df['Name'] == tutor) & (df['Schedule'] == option)].to_list()
            # df.loc[index[0], 'Available'] = 'N' # it's not available anymore!
            # df.loc[index[0], 'Student Email'] = email
    
            #Name	Subject	Email	Schedule	Date	Student Email
            rows = [[tutor, subject, email_, tutor_time, str(tutor_date), email, 'N', 'N']]
            mailing(tutor, subject, email_, tutor_time, str(tutor_date), email)
            df = pd.concat([df, pd.DataFrame(rows, columns=df.columns.values.tolist())])
            wks_schedule.update([df.columns.values.tolist()] + df.values.tolist())
            st.success('You are booked! Please check your email for the confirmation', icon="✅")
        elif check_.shape[0] == 0:
            st.error('Your email address is not found in our system. Please register from the main website first', icon="🚨")

else:
    st.write('Please choose your tutor')



    
# pw = '@RQu&S56pAS1'


