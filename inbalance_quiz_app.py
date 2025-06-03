import streamlit as st
from PIL import Image
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Page setup
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# Session state initialization
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "completed" not in st.session_state:
    st.session_state.completed = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "email" not in st.session_state:
    st.session_state.email = ""

# Load logo
st.image("logo.png", width=100)
st.markdown("<h1 style='text-align: center; color: teal;'>Check Your Hormonal Balance</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>A 1-minute quiz to understand if your symptoms might suggest PCOS, insulin resistance, or hormonal imbalance.</p>", unsafe_allow_html=True)

# Email validator
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Name & email form
if st.session_state.q_index == 0 and not st.session_state.completed:
    st.markdown("### 👋 Let's start with a few details")
    st.session_state.name = st.text_input("Your first name")
    st.session_state.email = st.text_input("Your email")

    if st.button("Start Quiz"):
        if not st.session_state.name.strip():
            st.warning("Please enter your name.")
        elif not is_valid_email(st.session_state.email):
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.q_index = 1
            st.rerun()
    st.stop()

# Quiz Questions
questions = [
    {
        "question": "How regular was your menstrual cycle in the past year?",
        "options": [
            ("Does not apply (hormonal treatments/pregnancy)", 0),
            ("Regular most of the time (25–35 days)", 1),
            ("Often irregular (<25 or >35 days)", 6),
            ("I rarely got my period this year (<6 times)", 8),
        ],
    },
    {
        "question": "Do you notice excessive thick black hair growth on your face, chest, or back?",
        "options": [
            ("No, not at all", 1),
            ("Yes, but controlled with hair removal", 5),
            ("Yes, and resistant to removal", 7),
            ("Yes, and also hair thinning on scalp", 8),
        ],
    },
    {
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            ("No, not really", 1),
            ("Yes, but controlled", 4),
            ("Yes, often despite treatment", 6),
            ("Yes, severe and resistant", 8),
        ],
    },
    {
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            ("No, weight is stable", 1),
            ("Mostly stable with effort", 2),
            ("Struggling without big diet/exercise changes", 5),
            ("Struggling even with diet and exercise", 7),
        ],
    },
    {
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            ("No, not really", 1),
            ("Sometimes after heavy/sugary meals", 2),
            ("Yes, often regardless of what I eat", 4),
            ("Yes, almost daily", 6),
        ],
    },
]

# Quiz Logic
index = st.session_state.q_index

if index <= len(questions):
    if index < len(questions):
        q = questions[index]
        st.markdown(f"<h4 style='font-weight: bold;'>{q['question']}</h4>", unsafe_allow_html=True)
        selected = st.radio(" ", [opt[0] for opt in q["options"]], key=f"q_{index}")
        if st.button("Next"):
            score = next(val for txt, val in q["options"] if txt == selected)
            st.session_state.answers.append(score)
            st.session_state.q_index += 1
            st.rerun()
    else:
        st.markdown("**Would you like to join our app waitlist for expert hormonal tracking?**")
        waitlist_choice = st.radio("Join waitlist?", ["Yes", "No"], key="waitlist")

        if waitlist_choice == "Yes":
            track_method = st.radio(
                "Do you currently track your cycle or symptoms?",
                ["Yes, with an app", "Yes, manually", "No, but I want to", "No, and I don’t know where to start", "Other"]
            )
            symptoms = st.multiselect(
                "What symptoms do you deal with most often?",
                ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"]
            )
            goal = st.radio(
                "What is your main health goal right now?",
                ["Understand my cycle", "Reduce symptoms", "Find medical answers", "Create a personalized plan", "Just curious", "Other"]
            )
            extra_notes = st.text_area("Anything else you'd like to share?")

            st.session_state.extra = {
                "Track Method": track_method,
                "Symptoms": ", ".join(symptoms),
                "Goal": goal,
                "Notes": extra_notes
            }

        if st.button("Finish Quiz"):
            st.session_state.completed = True
            st.rerun()

# Final Results
if st.session_state.completed:
    total = sum(st.session_state.answers)
    name = st.session_state.name
    email = st.session_state.email

    if total < 8:
        diag = "No strong hormonal patterns detected"
        msg = "You don’t currently show strong signs of hormonal dysfunction — but it’s smart to keep monitoring changes."
    elif total < 16:
        diag = "Ovulatory Imbalance"
        msg = "You may have mild cycle or ovulation issues like fatigue, acne, or irregular cycles."
    elif total < 24:
        diag = "HCA-PCO (Possible PCOS)"
        msg = "You show signs of PCOS — such as irregular cycles, excess androgens, or insulin-related symptoms."
    else:
        diag = "H-PCO (Androgenic + Metabolic)"
        msg = "You may have both hormonal and metabolic symptoms seen in PCOS and insulin resistance."

    st.success("✅ Done! Here's your analysis:")
    st.markdown(f"<h3 style='color: teal;'>🧬 Result: {diag}</h3>", unsafe_allow_html=True)
    st.write(msg)

    st.info("💡 How InBalance Can Help")
    st.markdown("""
    InBalance helps you track symptoms, cycles, skin/hair changes, energy and weight — so our expert team can guide you.

    Whether you’re confirming a diagnosis, adjusting nutrition, or optimizing workouts — we’ve got your back.
    """)

    st.image("qr_code.png", width=150)

    # Save to Google Sheets
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        sheet = client.open(st.secrets["google_sheets"]["sheet_name"])
        worksheet = sheet.worksheet(st.secrets["google_sheets"]["worksheet_name"])

        # Compose row
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, name, email, total, diag, msg]
        if "extra" in st.session_state:
            extra = st.session_state.extra
            row += [extra.get("Track Method", ""), extra.get("Symptoms", ""), extra.get("Goal", ""), extra.get("Notes", "")]
        else:
            row += ["", "", "", ""]

        worksheet.append_row(row)
        st.success("📥 Your results were saved successfully!")
    except Exception as e:
        st.error("❌ Could not save data to Google Sheets.")
        st.text(str(e))

    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()
