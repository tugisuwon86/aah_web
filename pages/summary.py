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
        Page("pages/tutor_signup.py", "Tutor Sign Up"),

        Section(name="Class Update", icon="💪"),    
        # Page("pages/cancel_session.py", "Student Registration"),
        Page("pages/complete_session.py", "Follow up"),
        Page("pages/summary.py", "Summary"),
    ]
)
add_page_title() # By default this also adds indentation

meta_col0, meta_col1, meta_col2 = st.columns(3)
# ---------------------------------------------------------------------------------------------------------
                
# ---------------------------------------------------------------------------------------------------------
## ADMIN!
admins = {"tugisuwon@gmail.com": "123456",
         }

# Read data from google sheets to initiate
import gspread

credentials = st.secrets['gcp_service_account']
sa = gspread.service_account_from_dict(credentials)
sh = sa.open("AAh schedules")

wks_schedule = sh.worksheet("Tutor Student Matching")

# read google sheets as dataframe
df = pd.DataFrame(wks_schedule.get_all_records())
df = df[(df['Tutor Confirm'] == 'Y') & (df['Student Confirm'] == 'Y')]
tutors = ["All"] + list(set(df.Name.values))

email = st.text_input('Please type your admin email')
password = st.text_input('Password')
st.write('Your email address is: ', email)

import datetime as dt
if email in admins and admins[email] == password:
    NOW = (dt.datetime.utcnow()).replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = meta_col0.date_input("Start Date", (NOW-dt.timedelta(days=730)).date(), min_value=(NOW-dt.timedelta(days=730)).date(), max_value=NOW)
    end_date = meta_col1.date_input("End Date", NOW, min_value=(NOW-dt.timedelta(days=730)).date(), max_value=NOW)
    tutor_name = "All" #meta_co2.selectbox("Select tutor", tutors)
    st.write(tutors)
    st.write(start_date, end_date)
    st.write(list(df.columns))
    df = df[(df['Date'] >= str(start_date)[:10]) & (df['Date'] <= str(end_date)[:10])]
    if tutor_name != "All":
        df = df[df['Name'] == tutor_name]
    st.dataframe(df)
    if df.shape[0] > 0:
        df_summary = df.groupby(['Name'])['Name'].count().reset_index()
        df_summary.columns = ['Name', '# of Hours Tutored']
    
        st.dataframe(df_summary)
    else:
        st.write('No record found')
    
elif email not in admins:
    st.error("You are not one of our admins")
elif email in admins and admins[email] != password:
    st.error("Wrong password")

