# run every hour

import streamlit as st
#from streamlit_pandas_profiling import st_profile_report
import pandas as pd
import re
import json
import time

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

def mailing(subject, name, email_, cat='tutor'):
    import smtplib
    from email.mime.text import MIMEText
    if cat == 'tutor':
        msg = MIMEText(f"""
        Hello {name}, 
    
        Your account is now active. Please visit https://aah-tutors.streamlit.app/Tutor%20Availability%20Update to add/update your schedule for tutoring. 
    
        
        """[1:])
    elif cat == 'student':
        msg = MIMEText(f"""
        Hello {name}, 
    
        Your account is now active. Please visit https://aah-tutors.streamlit.app/Sign%20up%20for%20a%20session to sign up for your first session.
    
        
        """[1:])
    msg['Subject'] = 'AAH Account Approval'
    connection = smtplib.SMTP('smtp.gmail.com', 587)
    connection.starttls()
    connection.login('aahtutoringscheduler@gmail.com','qdqrhbtswkkemzlw')#'lnafzpcllnnpwtmk') #'@RQu&S56pAS1')
    connection.sendmail('aahtutoringscheduler@gmail.com', email_, msg.as_string())
    connection.quit()


# Read data from google sheets to initiate
import gspread

credentials = st.secrets['gcp_service_account']
sa = gspread.service_account_from_dict(credentials)
sh = sa.open("AAh schedules")

wks_tutor = sh.worksheet("Tutors_Registration")
wks_student = sh.worksheet("Students_Registration")

# read google sheets as dataframe
df_student = pd.DataFrame(wks_student.get_all_records())
df_tutor = pd.DataFrame(wks_tutor.get_all_records())

index = 0
while True:
  output = []
  for row in df_tutor.values:
      email_ = row[2]
      name_ = row[0]
      if row[-2] == 'Y' and row[-1] == 'N':
          #st.write(row)
          mailing('', name_, email_)
          row[-1] = 'Y'
      output += [row]
  df_tutor = pd.DataFrame(output, columns = df_tutor.columns)
  wks_tutor.update([df_tutor.columns.values.tolist()] + df_tutor.values.tolist())
  #st.write("Email sent to tutors")
  
  output = []
  for row in df_student.values:
      email_ = row[2]
      name_ = row[0]
      if row[-2] == 'Y' and row[-1] == 'N':
          mailing('', name_, email_, 'student')
          row[-1] = 'Y'
      output += [row]
  df_student = pd.DataFrame(output, columns = df_student.columns)
  wks_student.update([df_student.columns.values.tolist()] + df_student.values.tolist())
  #st.write("Email sent to students")
  st.write('test!' + ' ' + str(index))
  index += 1
  time.sleep(15)
    
