import streamlit as st
from email.message import EmailMessage
import smtplib
import traceback

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Work Values Test", layout="centered")

# -------------------------------------------------
# CALLBACK FOR BUTTONS
# -------------------------------------------------
def set_response(q_idx, value):
    st.session_state.responses[q_idx] = value

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "show_test" not in st.session_state:
    st.session_state.show_test = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "email_sent" not in st.session_state:
    st.session_state.email_sent = False
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "info" not in st.session_state:
    st.session_state.info = {}
if "scores" not in st.session_state:
    st.session_state.scores = {}

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.title("Work Values Assessment")

# -------------------------------------------------
# USER INFO FORM
# -------------------------------------------------
with st.form("info_form"):
    Name = st.text_input("Full Name")
    Age = st.number_input("Age", min_value=10, max_value=100, step=1)
    Education = st.text_input("Education")
    School = st.text_input("School / University")
    Subjects = st.text_input("Subjects")
    Hobbies = st.text_area("Hobbies")
    Dream = st.text_area("Your 'Impossible' Dream")
    Email = st.text_input("Email")
    Phone = st.text_input("Phone Number")

    start = st.form_submit_button("Start Test")

if start:
    st.session_state.info = {
        "Name": Name,
        "Age": Age,
        "Education": Education,
        "School": School,
        "Subjects": Subjects,
        "Hobbies": Hobbies,
        "Dream": Dream,
        "Email": Email,
        "Phone": Phone
    }
    st.session_state.show_test = True

if not st.session_state.show_test:
    st.stop()

# -------------------------------------------------
# QUESTIONS (Work Values)
# -------------------------------------------------
questions = [
    ("I feel fulfilled when I know my work benefits other people.", "Purpose & Social Impact"),
    ("I want a career that lets me make a difference in the world.", "Purpose & Social Impact"),
    ("Helping others is more important to me than earning a high salary.", "Purpose & Social Impact"),
    ("I would enjoy solving problems that affect my community or society.", "Purpose & Social Impact"),
    ("I prefer working on tasks where I can decide how to get them done.", "Autonomy & Creativity"),
    ("I enjoy coming up with new ideas and creative solutions.", "Autonomy & Creativity"),
    ("I would rather have a flexible role than one with strict rules.", "Autonomy & Creativity"),
    ("I like thinking outside the box, even if it means taking risks.", "Autonomy & Creativity"),
    ("I enjoy tasks that push me to learn new things.", "Growth & Challenge"),
    ("I want a job that helps me grow both personally and professionally.", "Growth & Challenge"),
    ("I get bored doing the same type of work for a long time.", "Growth & Challenge"),
    ("I am motivated by challenging goals.", "Growth & Challenge"),
    ("I prefer jobs that have a fixed routine and long-term security.", "Stability & Security"),
    ("Knowing that my job is stable is very important to me.", "Stability & Security"),
    ("I value a career that offers steady income and clear expectations.", "Stability & Security"),
    ("I would rather avoid careers that are unpredictable or risky.", "Stability & Security"),
    ("I want to work in a field where I can earn respect from others.", "Recognition & Advancement"),
    ("I am motivated by promotions and career advancement.", "Recognition & Advancement"),
    ("I like being recognized for my achievements.", "Recognition & Advancement"),
    ("I want to be in a career where I can reach a high position.", "Recognition & Advancement"),
    ("I enjoy being part of a team where people support each other.", "Collaboration & Belonging"),
    ("I want a workplace where I feel like I belong.", "Collaboration & Belonging"),
    ("I do my best work when I collaborate with others.", "Collaboration & Belonging"),
    ("I prefer environments where people value kindness and empathy.", "Collaboration & Belonging"),
    ("It is important for me to have time for my personal life outside of work.", "Lifestyle & Flexibility"),
    ("I want a job that allows for a flexible schedule.", "Lifestyle & Flexibility"),
    ("I would rather have a job with balance than one that takes up all my time.", "Lifestyle & Flexibility"),
    ("I value being able to decide when and where I work.", "Lifestyle & Flexibility"),
    ("I would enjoy starting something of my own instead of working for someone else.", "Entrepreneurial Drive"),
    ("I like taking initiative and turning ideas into action.", "Entrepreneurial Drive"),
    ("I prefer work where I can take risks and make bold decisions.", "Entrepreneurial Drive"),
    ("I would rather create new solutions than follow existing methods.", "Entrepreneurial Drive")
]

st.header("Rate each statement (1 = Strongly Disagree, 5 = Strongly Agree)")

# -------------------------------------------------
# BUTTONS RENDER
# -------------------------------------------------
for idx, (q, category) in enumerate(questions):
    st.write(f"**{q}**")

    if idx not in st.session_state.responses:
        st.session_state.responses[idx] = 0

    cols = st.columns(5)
    for val in range(1, 6):
        with cols[val - 1]:
            st.button(
                str(val),
                key=f"q{idx}_{val}",
                on_click=set_response,
                args=(idx, val)
            )

            if st.session_state.responses[idx] == val:
                st.markdown(
                    """
                    <div style="
                        height:6px;
                        background-color:#ff2b2b;
                        margin-top:4px;
                        border-radius:4px;">
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# -------------------------------------------------
# SUBMIT BUTTON
# -------------------------------------------------
all_answered = len(st.session_state.responses) == len(questions) \
               and all(v > 0 for v in st.session_state.responses.values())

submit = st.button("Submit Test", disabled=not all_answered)

# -------------------------------------------------
# PROCESS SUBMISSION
# -------------------------------------------------
if submit and not st.session_state.submitted:
    scores = {}
    for _, category in questions:
        scores[category] = 0

    for idx, (_, category) in enumerate(questions):
        scores[category] += st.session_state.responses[idx]

    st.session_state.scores = scores
    st.session_state.submitted = True

# -------------------------------------------------
# EMAIL LOGIC
# -------------------------------------------------
if st.session_state.submitted and not st.session_state.email_sent:
    info = st.session_state.info
    scores = st.session_state.scores

    email_body = f"""
Name: {info['Name']}
Age: {info['Age']}
Education: {info['Education']}
School: {info['School']}
Subjects: {info['Subjects']}
Hobbies: {info['Hobbies']}
Dream: {info['Dream']}
Email: {info['Email']}
Phone: {info['Phone']}

--- WORK VALUES SCORES ---
"""
    for cat, score in scores.items():
        email_body += f"{cat}: {score}\n"

    email_body += "\n--- Detailed Responses ---\n"
    for idx, (q, category) in enumerate(questions):
        email_body += f"{q} [{category}]: {st.session_state.responses[idx]}\n"

    try:
        sender = st.secrets["EMAIL"]
        receiver = st.secrets["RECEIVER"]
        password = st.secrets["EMAIL_PASSWORD"]
    except Exception:
        st.error("Missing EMAIL, RECEIVER, or EMAIL_PASSWORD in Streamlit secrets.")
        st.stop()

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = f"Work Values Test Results – {info['Name']}"
    msg.set_content(email_body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        st.session_state.email_sent = True
    except Exception:
        st.error("Failed to send email.")
        st.code(traceback.format_exc())
        st.stop()

# -------------------------------------------------
# FINAL CONFIRMATION
# -------------------------------------------------
if st.session_state.email_sent:
    st.success(
        "Your results have been securely sent to Tripti Chapper Careers Counselling.\n"
        "Please contact them to receive your personalized report."
    )
