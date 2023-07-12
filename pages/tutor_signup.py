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

# ---------------------------------------------------------------------------------------------------------
meta_col0, meta_col1, meta_col2 = st.columns(3)
# ---------------------------------------------------------------------------------------------------------
                
# Create a dictionary with country name and corresponding timezone
timezone_dict = {
    "North America": {
        "United States": "America/New_York",
        "Canada": "America/Toronto",
        "Mexico": "America/Mexico_City",
        "Jamaica": "America/Jamaica",
        "Costa Rica": "America/Costa_Rica",
        "Bahamas": "America/Nassau",
        "Honduras": "America/Tegucigalpa",
        "Cuba": "America/Havana",
        "Dominican Republic": "America/Santo_Domingo"
    },
    "South America": {
        "Brazil": "America/Sao_Paulo",
        "Argentina": "America/Argentina/Buenos_Aires",
        "Chile": "America/Santiago",
        "Colombia": "America/Bogota",
        "Peru": "America/Lima",
        "Uruguay": "America/Montevideo",
        "Ecuador": "America/Guayaquil",
        "Bolivia": "America/La_Paz",
        "Paraguay": "America/Asuncion",
        "Venezuela": "America/Caracas"
    },
    "Europe": {
        "United Kingdom": "Europe/London",
        "France": "Europe/Paris",
        "Germany": "Europe/Berlin",
        "Italy": "Europe/Rome",
        "Spain": "Europe/Madrid",
        "Russia": "Europe/Moscow",
        "Turkey": "Europe/Istanbul",
        "Greece": "Europe/Athens",
        "Poland": "Europe/Warsaw",
        "Ukraine": "Europe/Kiev"
    },
    "Asia": {
        "India": "Asia/Kolkata",
        "Japan": "Asia/Tokyo",
        "China": "Asia/Shanghai",
        "Saudi Arabia": "Asia/Riyadh",
        "South Korea": "Asia/Seoul",
        "Indonesia": "Asia/Jakarta",
        "Malaysia": "Asia/Kuala_Lumpur",
        "Vietnam": "Asia/Ho_Chi_Minh",
        "Philippines": "Asia/Manila",
        "Thailand": "Asia/Bangkok"
    },
    "Oceania": {
        "Australia": "Australia/Sydney",
        "New Zealand": "Pacific/Auckland",
        "Fiji": "Pacific/Fiji",
        "Papua New Guinea": "Pacific/Port_Moresby",
        "Samoa": "Pacific/Apia",
        "Tonga": "Pacific/Tongatapu",
        "Solomon Islands": "Pacific/Guadalcanal",
        "Vanuatu": "Pacific/Efate",
        "Kiribati": "Pacific/Tarawa",
        "New Caledonia": "Pacific/Noumea"
    }
}

# Create a list of continents
continents = ["North America", "South America", "Europe", "Asia", "Oceania"]

# Streamlit app page setup
st.set_page_config(
    page_title='Time Zone Coverter', 
    page_icon='🌎',
    layout='centered',
    initial_sidebar_state='expanded',
    menu_items={
        'About': """This app is intended to select a country, get its 
        time zone in UTC format  and have its correspondent result 
        from a user-entered PST time."""
    }  
)

# Main header
st.header('Time Zone Coverter Streamlit app')

# Add some blank space
st.markdown("##")

# Create a dropdown to select a continent
continent = st.sidebar.selectbox("1. Select a continent", continents)

# Create a dropdown to select a country within the selected continent
countries = list(timezone_dict[continent].keys())
country = st.sidebar.selectbox("2. Select a country", countries)

# Display the selected UTC offset
st.markdown("### :earth_americas: Corresponding UTC time:")
timezone = timezone_dict[continent][country]
utc_offset = datetime.now(pytz.timezone(timezone)).strftime('%z')
st.markdown(f"> **{country}** time zone is **UTC{utc_offset[:-2]}:{utc_offset[-2:]}**")

# # Add some blank space
# st.markdown("##")

# # Create input for PST time
# st.markdown("### :clock10: PST time to UTC converter:")
# pst_input = st.text_input("Enter PST time (e.g., 10:00 AM PST)")

# # Convert PST time to UTC+X (where X is the offset)
# try:
#     pst_time = datetime.strptime(pst_input, "%I:%M %p PST")
#     pst_time = pytz.timezone("US/Pacific").localize(pst_time, is_dst=None)
#     target_time = pst_time.astimezone(pytz.timezone(timezone)).strftime("%I:%M %p %Z")
#     st.markdown(f"> The corresponding time in **{country}** is **{target_time}**")
# except:
#     st.markdown("""
#     :lock: Invalid input format. Please enter PST time in format 
#     '<span style="color:#7ef471"><b> 10:00 AM PST </b></span>'
#     """, unsafe_allow_html=True)
    
# ---------------------------------------------------------------------------------------------------------
# Read data from google sheets to initiate
import gspread

credentials = st.secrets['gcp_service_account']
sa = gspread.service_account_from_dict(credentials)
sh = sa.open("AAh schedules")

wks_schedule = sh.worksheet("Tutor Weekly Schedule")
wks_tutor = sh.worksheet("Tutors_Registration")
wks_student = sh.worksheet('Students_Registration')

# read google sheets as dataframe
df = pd.DataFrame(wks_schedule.get_all_records())
df_tutor = pd.DataFrame(wks_tutor.get_all_records())
df_student = pd.DataFrame(wks_student.get_all_records())

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

subject_options = sorted(tuple(set(df['Subject'].values)))
subject = meta_col0.selectbox('Subject', subject_options)

NOW = (dt.datetime.utcnow()).replace(hour=0, minute=0, second=0, microsecond=0)
tutor_date = meta_col1.date_input("Tutor Date", NOW, min_value=NOW, max_value=(NOW+dt.timedelta(days=14)).date())

tutor_option = df.loc[(df['Subject']==subject) & (df['Schedule'].str.startswith('M'))].Name.unique()
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


