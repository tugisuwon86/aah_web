import streamlit as st
#from streamlit_pandas_profiling import st_profile_report
import pandas as pd
import pandas_profiling
from datetime import datetime
import datetime as dt
import pytz

st.markdown("""
    <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 250px;
        }
    </style>
    """, unsafe_allow_html=True)

st.title('AAH Tutor Scheduler')

meta_col0, meta_col1, meta_col2 = st.columns(3)
# ---------------------------------------------------------------------------------------------------------
                
# ---------------------------------------------------------------------------------------------------------
# Read data from google sheets to initiate
import gspread

credentials = st.secrets['gcp_service_account']
sa = gspread.service_account_from_dict(credentials)
sh = sa.open("AAh schedules")

wks_schedule = sh.worksheet("Tutor Weekly Schedule")
wks_tutor = sh.worksheet("Tutors_Registration")
wks_student = sh.worksheet('Students_Registration')
wks_absense = sh.worksheet("Tutors Absense")

# read google sheets as dataframe
df = pd.DataFrame(wks_schedule.get_all_records())
df_tutor = pd.DataFrame(wks_tutor.get_all_records())
# filter by completed registration
df_tutor = df_tutor[df_tutor['complete'] == 'Y']

df_student = pd.DataFrame(wks_student.get_all_records())
df_abs = pd.DataFrame(wks_absense.get_all_records())

email = st.text_input('Please type your email (must match with email we have in our system')
st.write('Your email address is: ', email)
st.write('Make sure your email address if accurate before proceeding; otherwise, you will not be able to sign up for tutor')

st.write('Your status summary---------')
# make sure the student is in our system
check_ = df_student[(df_student['email'] == email) & (df_student['complete'] == 'Y')]
number_of_booking = df[df['Student Email'] == email]
if check_.shape[0] == 0:
    st.error('Your email address is not found in our system. Please register from the main website first', icon="🚨")
elif number_of_booking.shape[0] >= 2:
    current_booking = number_of_booking[['Name', 'Subject', 'Schedule']]
    current_booking.columns = ['Tutor Name', 'Subject', 'Schedule']
    st.table(current_booking)
    st.error('You booked more than the number of weekly limit')

#subject_options = sorted(tuple(set(df['Subject'].values)))
subject = meta_col0.selectbox('Subject', ["Elementary Math", "Pre-Calculus"])

NOW = (dt.datetime.utcnow()).replace(hour=0, minute=0, second=0, microsecond=0)
tutor_date = meta_col1.date_input("Tutor Date", NOW, min_value=NOW, max_value=(NOW+dt.timedelta(days=14)).date())

tutor_option = df_tutor.loc[((df_tutor['math_subjects'].contains(subject)) | (df_tutor['english_subjects'].contains(subject))) & (df_tutor['Schedule'].str.startswith('M'))].Name.unique()
tutor = meta_col2.selectbox('Tutor', tutor_option)

# ---------------------------------------------------------------------------------------------------------


temp = df.loc[(df['Name']==tutor) & (df['Schedule'].str.contains('M'))]
available_options = temp[temp['Available'] == 'Y']

option = st.selectbox('Please choose the time slot you want to schedule: ', sorted(available_options['Schedule'].values))
st.write('You selected: ', option)

with st.form('save_form'):
    save_submitted = st.form_submit_button('Please click to book the slot')

# make sure the student is in our system
check_ = df_student[(df_student['email'] == email) & (df_student['complete'] == 'Y')]
print(check_, tutor, option)
print(df.head())

if save_submitted:
    if number_of_booking.shape[0] >= 2:
        st.error('You booked more than the number of weekly limit', icon="🚨")
    elif check_.shape[0] > 0:
        index = df.index[(df['Name'] == tutor) & (df['Schedule'] == option) & (df['Available'] == 'Y')].to_list()
        df.loc[index[0], 'Available'] = 'N' # it's not available anymore!
        df.loc[index[0], 'Student Email'] = email
        wks_schedule.update([df.columns.values.tolist()] + df.values.tolist())
        st.success('You are booked! Please check your email for the confirmation', icon="✅")
    elif check_.shape[0] == 0:
        st.error('Your email address is not found in our system. Please register from the main website first', icon="🚨")


