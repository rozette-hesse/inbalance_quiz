import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# --------------- CONFIG ----------------
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
logo = Image.open("logo.png")
st.image(logo, width=120)

# --------------- SESSION INIT ---------------
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.answers = {}
    st.session_state.waitlist = {}
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --------------- GOOGLE SHEETS ---------------
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except Exception as e:
    st.error("Google Sheet not connected.")
    sheet = None

# --------------- QUESTIONS ----------------
questions = {
    "Q1": {
        "text": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (e.g., hormonal treatment or pregnancy)",
            "Regular (25–35 days)",
            "Often irregular (< 25 or > 35 days)",
            "Rarely got period (< 6 times a year)"
        ]
    },
    "Q2": {
        "text": "Do you notice excessive thick black hair on your face, chest, or back?",
        "options": [
            "No, not at all",
            "Yes, manageable with hair removal",
            "Yes, resistant to hair removal",
            "Yes + scalp thinning or hair loss"
        ]
    },
    "Q3": {
        "text": "Have you had acne or oily skin this year?",
        "options": [
            "No",
            "Yes, mild but manageable",
            "Yes, often despite treatment",
            "Yes, severe and persistent"
        ]
    },
    "Q4": {
        "text": "Have you experienced weight changes?",
        "options": [
            "No, stable weight",
            "Stable only with effort",
            "Struggling to maintain weight",
            "Can't lose weight despite diet/exercise"
        ]
    },
    "Q5": {
        "text": "Do you feel tired or sleepy after meals?",
        "options": [
            "No, not really",
            "Sometimes after heavy meals",
            "Yes, often regardless of food",
            "Yes, almost daily with alertness issues"
        ]
    }
}

# ------------- UTILS -------------
def get_country_choices():
    countries = []
    for country in pycountry.countries:
        code = phonenumbers.country_code_for_region(country.alpha_2)
        if code:
            emoji = chr(127397 + ord(country.alpha_2[0])) + chr(127397 + ord(country.alpha_2[1]))
            countries.append(f"{emoji} {country.name} (+{code})")
    countries = sorted(set(countries))
    return countries

def validate_phone(country, number):
    try:
        country_code = country.split("(+")[1].split(")")[0]
        phone_obj = phonenumbers.parse(f"+{country_code}{number}")
        return phonenumbers.is_valid_number(phone_obj)
    except:
        return False

# ------------- PAGE: INTRO -------------
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1-minute quiz to understand your hormonal health — and how InBalance can help.")

    first_name = st.text_input("👩‍🦰 First Name")
    last_name = st.text_input("👩‍🦰 Last Name")
    email = st.text_input("📧 Email")
    countries = get_country_choices()
    country = st.selectbox("🌍 Country", countries)
    phone = st.text_input("📱 Phone (without spaces)")

    if st.button("Start Quiz"):
        if not all([first_name.strip(), last_name.strip(), email.strip(), phone.strip(), country]):
            st.warning("Please complete all fields.")
        elif not validate_phone(country, phone):
            st.warning("Invalid phone number for selected country.")
        else:
            st.session_state.info = {
                "First Name": first_name,
                "Last Name": last_name,
                "Email": email,
                "Country": country,
                "Phone": phone
            }
            st.session_state.page = "quiz"
            st.rerun()

# ------------- PAGE: QUIZ -------------
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    for key, q in questions.items():
        st.session_state.answers[key] = st.radio(
            f"**{q['text']}**", q["options"], key=key, index=None
        )

    if st.button("Submit Answers"):
        if None in st.session_state.answers.values():
            st.warning("Please answer all questions before continuing.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ------------- PAGE: RESULTS -------------
elif st.session_state.page == "results":
    st.header("🍭 Diagnosis")
    q = list(st.session_state.answers.values())
    # simple scoring logic
    score = sum([i for i, ans in enumerate(q) if ans != q[0]])  # dummy score
    if q[0] in ["Often irregular (< 25 or > 35 days)", "Rarely got period (< 6 times a year)"]:
        diagnosis = "Cycle Irregularity"
    elif "resistant" in q[1] or "scalp" in q[1]:
        diagnosis = "Potential PCOS"
    elif "Can't lose weight" in q[3]:
        diagnosis = "H-PCO (Hormonal and Metabolic)"
    else:
        diagnosis = "Mild imbalance or no clear pattern"

    st.subheader(f"🧬 Diagnosis: {diagnosis}")
    st.markdown("### 🛠️ Recommendations based on your responses:")
    recs = []

    if "irregular" in q[0].lower():
        recs.append("Track your cycle phases daily to help identify ovulatory issues.")
    if "resistant" in q[1] or "scalp" in q[1]:
        recs.append("Hair changes may indicate excess androgens — our endocrinologists can help.")
    if "acne" in q[2] or "oily" in q[2]:
        recs.append("Persistent acne can reflect hormone imbalance — our clinicians guide you.")
    if "Struggling" in q[3] or "Can't lose weight" in q[3]:
        recs.append("Metabolic resistance may need lifestyle adjustments tailored to you.")
    if "sleepy" in q[4] or "fatigue" in q[4]:
        recs.append("Post-meal fatigue may link to sugar dips — a blood sugar plan helps.")

    for r in recs:
        st.info(r)

    st.warning("⚠️ *Information only. Always consult a physician for diagnosis.*")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 Precision tracking of symptoms & phases  
- 📊 Personalized recommendations based on cycle phase  
- 🩺 Direct access to gynecologists, endocrinologists, nutritionists & trainers  
- 🔁 Ongoing support and expert guidance  
- 💬 Everything tracked and adjusted in-app
""")
    st.image("qr_code.png", width=140)

    st.session_state.page = "waitlist"
    st.rerun()

# ------------- PAGE: WAITLIST -------------
elif st.session_state.page == "waitlist":
    st.subheader("💬 Want to join the InBalance waitlist?")
    join = st.radio("Would you like to join?", ["Yes", "No"], index=None)
    tracking = symptoms = goal = notes = ""

    if join == "Yes":
        tracking = st.radio("Do you track your cycle/symptoms?", ["Yes, with an app", "Yes, manually", "Not yet", "Other"], index=None)
        symptoms = st.multiselect("Top symptoms:", ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog"])
        goal = st.radio("Main health goal:", ["Understand my cycle", "Reduce symptoms", "Get diagnosis", "Personalized plan", "Just curious"], index=None)
        notes = st.text_area("Other notes:")

    if st.button("📩 Finish & Save"):
        try:
            if sheet:
                row = [
                    st.session_state.timestamp,
                    *st.session_state.info.values(),
                    *st.session_state.answers.values(),
                    diagnosis,
                    join,
                    tracking,
                    ", ".join(symptoms),
                    goal,
                    notes
                ]
                sheet.append_row(row)
                st.success("✅ Saved! We’ll be in touch 💌")
            else:
                st.error("❌ Could not connect to Google Sheet.")
        except Exception as e:
            st.error(f"Error saving: {e}")

    if st.button("🔁 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
