import streamlit as st
from PIL import Image
import re
import pycountry
import phonenumbers
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ---------------- CONFIG ----------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# ---------------- SESSION INIT ----------------
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

# ---------------- COUNTRY CODES + FLAGS ----------------
def get_country_options():
    countries = []
    for country in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(country.alpha_2)
            flag = chr(127397 + ord(country.alpha_2[0])) + chr(127397 + ord(country.alpha_2[1]))
            countries.append((f"{flag} +{code} ({country.name})", f"+{code}"))
        except:
            continue
    return sorted(list(set(countries)), key=lambda x: x[1])

country_options = get_country_options()
country_labels = [c[0] for c in country_options]
country_values = [c[1] for c in country_options]

# ---------------- GOOGLE SHEETS ----------------
try:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials_dict = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
    sheet = gspread.authorize(credentials).open("InBalance_Quiz_Responses").sheet1
except Exception:
    sheet = None

# ---------------- QUIZ QUESTIONS ----------------
questions = [
    {
        "q": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (e.g., hormonal treatment or pregnancy)",
            "Regular (25–35 days)",
            "Often irregular (< 25 or > 35 days)",
            "Rarely got period (< 6 times a year)"
        ]
    },
    {
        "q": "Do you notice excessive thick black hair on your face, chest, or back?",
        "options": [
            "No, not at all",
            "Yes, manageable with hair removal",
            "Yes, resistant to hair removal",
            "Yes + scalp thinning or hair loss"
        ]
    },
    {
        "q": "Have you had acne or oily skin this year?",
        "options": [
            "No",
            "Yes, mild but manageable",
            "Yes, often despite treatment",
            "Yes, severe and persistent"
        ]
    },
    {
        "q": "Have you experienced weight changes?",
        "options": [
            "No, stable weight",
            "Stable only with effort",
            "Struggling to maintain weight",
            "Can't lose weight despite diet/exercise"
        ]
    },
    {
        "q": "Do you feel tired or sleepy after meals?",
        "options": [
            "No, not really",
            "Sometimes after heavy meals",
            "Yes, often regardless of food",
            "Yes, almost daily with alertness issues"
        ]
    },
]

# ---------------- PERSONAL INFO ----------------
st.title("How Balanced Are Your Hormones?")
st.subheader("A 1-minute quiz to help you understand your hormonal health — and how InBalance can help.")

first_name = st.text_input("👩 First Name")
last_name = st.text_input("👩 Last Name")
email = st.text_input("📧 Email Address")

selected_label = st.selectbox("🌍 Country Code", country_labels)
country_code = country_options[country_labels.index(selected_label)][1]
phone_number = st.text_input("📱 Phone Number (no spaces)")

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email)

def is_valid_phone(code, number):
    try:
        parsed = phonenumbers.parse(code + number)
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

if st.button("Start Quiz"):
    if not first_name or not last_name:
        st.warning("Please enter your first and last name.")
    elif not is_valid_email(email):
        st.warning("Please enter a valid email.")
    elif not phone_number.strip().isdigit():
        st.warning("Phone must be numeric only.")
    elif not is_valid_phone(country_code, phone_number):
        st.warning("Phone number format is not valid for selected country.")
    else:
        st.session_state.quiz_started = True
        st.session_state.first_name = first_name
        st.session_state.last_name = last_name
        st.session_state.email = email
        st.session_state.country_code = country_code
        st.session_state.phone_number = phone_number
        st.session_state.answers = []
        st.session_state.waitlist_opt_in = None
        st.session_state.tracking = ""
        st.session_state.symptoms = []
        st.session_state.goal = ""
        st.session_state.notes = ""

# ---------------- QUIZ ----------------
if st.session_state.quiz_started:
    st.markdown("### 🧬 Your Hormonal Health Questions")
    answers = []
    for idx, q in enumerate(questions):
        st.markdown(f"**Q{idx + 1}: {q['q']}**")
        ans = st.radio("", q["options"], key=f"q{idx}", index=None)
        answers.append(ans)

    # ---------------- DIAGNOSIS LOGIC ----------------
    recommendations = []
    if answers[0] in ["Often irregular (< 25 or > 35 days)", "Rarely got period (< 6 times a year)"]:
        recommendations.append("📌 Your cycle seems irregular or infrequent. This could indicate hormonal disruptions or lack of ovulation.")
    if answers[2] in ["Yes, often despite treatment", "Yes, severe and persistent"]:
        recommendations.append("🧴 Chronic acne may point to underlying hormone or inflammation issues.")
    if answers[3] in ["Struggling to maintain weight", "Can't lose weight despite diet/exercise"]:
        recommendations.append("⚖️ You might be facing metabolic challenges — especially related to insulin or cortisol.")

    # ---------------- WAITLIST ----------------
    st.markdown("### 💬 Want to join the InBalance app waitlist?")
    waitlist_opt_in = st.radio("Would you like to join?", ["Yes", "No"], index=None)

    tracking = ""
    symptoms = []
    goal = ""
    notes = ""

    if waitlist_opt_in == "Yes":
        tracking = st.radio("How do you currently track your cycle?", [
            "Yes, with an app", "Yes, manually", "No, but I want to",
            "No, and I don’t know where to start", "Other"
        ], index=None)
        symptoms = st.multiselect("What symptoms do you deal with most often?", [
            "Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne",
            "Anxiety", "Sleep issues", "Brain fog", "Other"
        ])
        goal = st.radio("Your main health goal?", [
            "Understand my cycle", "Reduce symptoms", "Looking for diagnosis",
            "Personalized lifestyle plan", "Just curious", "Other"
        ], index=None)
        notes = st.text_area("Anything else you'd like us to know?")

    # ---------------- SUBMIT ----------------
    if st.button("📩 Finish & Save"):
        try:
            full_phone = st.session_state.country_code + st.session_state.phone_number
            if sheet:
                sheet.append_row([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    st.session_state.first_name,
                    st.session_state.last_name,
                    st.session_state.email,
                    full_phone,
                    *answers,
                    "\n".join(recommendations),
                    waitlist_opt_in,
                    tracking,
                    ", ".join(symptoms),
                    goal,
                    notes
                ])
                st.success("✅ Your responses were saved successfully!")
                st.markdown("## 🧬 Personalized Results & Guidance")
                for tip in recommendations:
                    st.markdown(f"- {tip}")
                st.image("qr_code.png", width=180)
            else:
                st.error("❌ Google Sheet not connected.")
        except Exception as e:
            st.error(f"❌ Could not save: {e}")
