import streamlit as st
import time
import numpy as np
import pandas as pd

st.set_page_config(page_title="Tutor Availability Sign up Form", page_icon="📈")

email = st.text_input('Please type your email (must match with email we have in our system')
st.write('Your email address is: ', email)
st.write('Make sure your email address if accurate before proceeding; otherwise, you will not be able to update your tutor schedule')


options_Monday = st.multiselect(
    "Please choose all available time slot for Monday (EST)",
    [str(i)+' PM -'+str(i+1) + ' PM' for i in range(3, 10)]
)

options_Tuesday = st.multiselect(
    "Please choose all available time slot for Tuesday (EST)",
    [str(i)+' PM -'+str(i+1) + ' PM' for i in range(3, 10)]
)

options_Wednesday = st.multiselect(
    "Please choose all available time slot for Wednesday (EST)",
    [str(i)+' PM -'+str(i+1) + ' PM' for i in range(3, 10)]
)

options_Thursday = st.multiselect(
    "Please choose all available time slot for Thursday (EST)",
    [str(i)+' PM -'+str(i+1) + ' PM'for i in range(3, 10)]
)

options_Friday = st.multiselect(
    "Please choose all available time slot for Friday (EST)",
    [str(i)+' PM -'+str(i+1) + ' PM' for i in range(3, 10)]
)

with st.form('save_form'):
    save_submitted = st.form_submit_button('Please click to update your schedule')


## create new dataframe with update schedule
# Read data from google sheets to initiate
import gspread

sa = gspread.service_account(filename='service_account.json')
sh = sa.open("AAh schedules")

wks_schedule = sh.worksheet("Tutor Weekly Schedule - next week")
wks_tutor = sh.worksheet("Tutors")

# read google sheets as dataframe
df = pd.DataFrame(wks_schedule.get_all_records())
df_tutor = pd.DataFrame(wks_tutor.get_all_records())

check_ = df_tutor[df_tutor['Email'] == email]
if check_.shape[0] > 0 and save_submitted:
    # clear worksheet first
    wks_schedule.clear()

    # overwrite if exists
    print(list(df.columns))
    df = df[df['Email'] != email]
    rows = []
    for dow, options in zip(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], [options_Monday, options_Tuesday, options_Wednesday, options_Thursday, options_Friday]):
        for r in options:
            rows += [['A', '', email, dow + ' : ' + r, 'Y']]
    schedule = pd.DataFrame(rows, columns=['Name', 'Subject', 'Email', 'Schedule', 'Available'])
    print(schedule.head(5))
    wks_schedule.update([schedule.columns.values.tolist()] + schedule.values.tolist())
    st.success('Your tutor availability schedule has been successfully updated!', icon="✅")
else:
    st.error('Your email address is not found in our system. Please register from the main website first', icon="🚨")