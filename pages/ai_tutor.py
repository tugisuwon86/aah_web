import streamlit as st
#from streamlit_pandas_profiling import st_profile_report
import pandas as pd
from datetime import datetime
import datetime as dt
import pytz
import json
import google.genai as genai
import os

# Configure the Gemini API client
# The st.secrets dictionary loads keys from Streamlit's secrets management 
# or a local .streamlit/secrets.toml file.
try:
    API_KEY = st.secrets['gemini_account']['api']
except KeyError:
    # Fallback to environment variable for local development outside Streamlit Cloud
    API_KEY = None
    if not API_KEY:
        st.error("Error: GEMINI_API_KEY not found. Please set it in secrets.toml or as an environment variable.")
        st.stop()

# Initialize the client
client = genai.Client(api_key=API_KEY)

# Streamlit Page Setup
st.set_page_config(page_title="Personalized AI Tutor", layout="wide")
st.title("🧠 Your Personalized AI Tutor (Gemini-Powered)")
st.caption("Ask me about any topic, and I'll explain it, quiz you, or help you practice!")


from st_pages import Page, Section, show_pages, add_page_title
show_pages(
    [
        Page("main.py", "Home", "🏠"),
        Section(name="For Tutors Only", icon="🎈️"),
        Page("pages/tutor_registration.py", "Tutor Registration"),
        Page("pages/tutor_availability.py", "Tutor Availability Update"),
        Page("pages/tutor_update.py", "Tutor Information Update"),
        
        Section(name="For Students Only", icon="💪"),    
        Page("pages/student_registration.py", "Student Registration"),
        Page("pages/tutor_signup.py", "Sign up for a session"),

        Section(name="Class Update", icon="💪"),    
        # Page("pages/cancel_session.py", "Student Registration"),
        Page("pages/complete_session.py", "Follow up"),
        Page("pages/summary.py", "Summary"),
        Page("pages/notification.py", "Notification"),
    ]
)
add_page_title() # By default this also adds indentation

meta_col0, meta_col1 = st.columns(2) #, meta_col2, meta_col3 = st.columns(4)
# ---------------------------------------------------------------------------------------------------------
                
# ---------------------------------------------------------------------------------------------------------


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
# elif number_of_booking.shape[0] >= 20:
#     st.error('You booked more than the number of weekly limit')

#subject_options = sorted(tuple(set(df['Subject'].values)))

# subjects_ = json.load(open('subjects.json'))
subjects_ = {'academic': ['English Conversation for International students', 'Elementary English & Language Arts', 
          'Middle School English & Language Arts', 'Elementary Math', 'Middle School Math', 'Pre-Algebra', 'Algebra I',
          'Algebra II', 'Geometry', 'Pre-Calculus', 'AP Calculus AB', 'AP Calculus BC', 'AP Physics', 'Beginner Spanish', 'Advanced Spanish', 
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

# 2. Model Configuration (System Prompt)
# ==============================================================================
# This is a critical step to define the AI's persona and rules.
SYSTEM_PROMPT = """
You are an encouraging and knowledgeable educational AI Tutor.
Your goal is to explain concepts clearly, provide practical examples, and engage the student 
through questions to check their understanding.

Tutor Rules:
1.  **Tone:** Be friendly, encouraging, and patient.
2.  **Explanations:** Break down complex topics into simple, digestible steps. Use real-world analogies.
3.  **Engagement:** After an explanation, always ask a simple, open-ended question or provide a short,
    thought-provoking quiz question to encourage active recall.
4.  **Corrections:** When the user makes a mistake, correct them kindly and explain *why* it was wrong,
    then gently re-route them back to the concept.
5.  **Language:** Use Markdown formatting for clear text, including bolding key terms.
"""
MODEL_NAME = 'gemini-2.5-flash'

# 3. Chat History Management
# ==============================================================================
# Initialize chat history in Streamlit's session state for persistence across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the Gemini Chat object with the history and system prompt
# We use the Chat service to manage the conversation context automatically.
if "chat_session" not in st.session_state:
    # Convert the System Prompt into a format the Chat Session can use
    system_instruction_part = genai.types.Part.from_text(SYSTEM_PROMPT)
    
    st.session_state.chat_session = client.chats.create(
        model=MODEL_NAME,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        )
    )
    # Add an initial welcome message to the display history
    st.session_state.messages.append(
        {"role": "assistant", "content": "Hello! I'm your AI Tutor. What subject or concept are you ready to learn about today?"}
    )
    
# 4. The Core Gemini API Call Function
# ==============================================================================
def generate_response(prompt):
    """Sends the user prompt to the Gemini Chat session and returns the response text."""
    try:
        # Use the chat_session.send_message, which automatically includes history
        response = st.session_state.chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, an error occurred: {e}"


# 5. Streamlit User Interface (UI)
# ==============================================================================

# Display existing messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask a question, or respond to the tutor..."):
    # Add user message to display history and show it in the app
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display the assistant's response
    with st.chat_message("assistant"):
        # Show a progress indicator while waiting for the AI
        with st.spinner("Thinking like a tutor..."):
            full_response = generate_response(prompt)
            st.markdown(full_response)
        
        # Add assistant response to display history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Optional: Add a button to reset the conversation
if st.sidebar.button("Reset Conversation"):
    # Clear both the display history and the underlying chat session
    st.session_state.messages = []
    del st.session_state.chat_session
    st.rerun()
        
    # pw = '@RQu&S56pAS1'
