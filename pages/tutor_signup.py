import streamlit as st
#from streamlit_pandas_profiling import st_profile_report
import pandas as pd
import pandas_profiling
from PIL import Image

st.markdown("""
    <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 250px;
        }
    </style>
    """, unsafe_allow_html=True)


st.title('AAH Tutor Scheduler')

# ---------------------------------------------------------------------------------------------------------
meta_col0, meta_col1, meta_col2 = st.columns(3)

# ---------------------------------------------------------------------------------------------------------
# Read data from google sheets to initiate
import gspread

credentials = st.secrets['gcp_service_account']
sa = gspread.service_account_from_dict(credentials)
sh = sa.open("AAh schedules")

wks_schedule = sh.worksheet("Tutor Weekly Schedule")
wks_tutor = sh.worksheet("Tutors")
wks_student = sh.worksheet('Students')

# read google sheets as dataframe
df = pd.DataFrame(wks_schedule.get_all_records())
df_tutor = pd.DataFrame(wks_tutor.get_all_records())
df_student = pd.DataFrame(wks_student.get_all_records())

email = st.text_input('Please type your email (must match with email we have in our system')
st.write('Your email address is: ', email)
st.write('Make sure your email address if accurate before proceeding; otherwise, you will not be able to sign up for tutor')

st.write('Your status summary---------')
# make sure the student is in our system
check_ = df_student[df_student['Email'] == email]
number_of_booking = df[df['Student Email'] == email]
if check_.shape[0] == 0:
    st.error('Your email address is not found in our system. Please register from the main website first', icon="🚨")
elif number_of_booking.shape[0] > 2:
    current_booking = number_of_booking[['Name', 'Subject', 'Schedule']]
    current_booking.columns = ['Tutor Name', 'Subject', 'Schedule']
    st.table(current_booking)
    st.error('You booked more than the number of weekly limit')

subject_options = sorted(tuple(set(df['Subject'].values)))
subject = meta_col0.selectbox('Subject', subject_options)

weekday_option = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
weekday = meta_col1.selectbox('Day of Week', weekday_option)

weekday_mapping = {'Monday': 'M', 'Tuesday': 'T', 'Wednesday': 'W'}


tutor_option = df.loc[(df['Subject']==subject) & (df['Schedule'].str.startswith(weekday_mapping[weekday]))].Name.unique()
tutor = meta_col2.selectbox('Tutor', tutor_option)

# ---------------------------------------------------------------------------------------------------------

## calendar view
from calendar_view.core import data
from calendar_view.core.config import CalendarConfig
from calendar_view.calendar import Calendar
from calendar_view.core.event import Event, EventStyles

config = data.CalendarConfig(
    lang='en',
    title=tutor,
    dates='',
    show_year=True,
    legend=False,
)
events = [
    Event('Planning', day='2019-09-23', start='11:00', end='13:00'),
    Event('Demo', day='2019-09-27', start='15:00', end='16:00'),
    Event('Retrospective', day='2019-09-27', start='17:00', end='18:00'),
]

data.validate_config(config)
data.validate_events(events, config)

calendar = Calendar.build(config)
calendar.add_events(events)
calendar.save("yoga_class.png")

image = Image.open("yoga_class.png")
st.image(image, caption='calendar')


temp = df.loc[(df['Name']==tutor) & (df['Schedule'].str.contains(weekday_mapping[weekday]))]
available_options = temp[temp['Available'] == 'Y']

option = st.selectbox('Please choose the time slot you want to schedule: ', sorted(available_options['Schedule'].values))
st.write('You selected: ', option)

with st.form('save_form'):
    save_submitted = st.form_submit_button('Please click to book the slot')

# make sure the student is in our system
check_ = df_student[df_student['Email'] == email]
print(check_, tutor, option)
print(df.head())

if check_.shape[0] > 0 and save_submitted:
    index = df.index[(df['Name'] == tutor) & (df['Schedule'] == option) & (df['Available'] == 'Y')].to_list()
    df.loc[index[0], 'Available'] = 'N' # it's not available anymore!
    df.loc[index[0], 'Student Email'] = email
    wks_schedule.update([df.columns.values.tolist()] + df.values.tolist())
    st.success('You are booked! Please check your email for the confirmation', icon="✅")
elif check_.shape[0] == 0:
    st.error('Your email address is not found in our system. Please register from the main website first', icon="🚨")


