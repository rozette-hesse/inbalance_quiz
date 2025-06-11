import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# --------------- CONFIG ---------------
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# --------------- STATE INITIALIZATION ---------------
if "step" not in st.session_state:
    st.session_state.step = "intro"
    st.session_state.info = {}
    st.session_state.answers = {}
    st.session_state.diagnosis = ""
    st.session_state.waitlist = {}
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --------------- GOOGLE SHEETS SETUP ---------------
try:
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except Exception:
    st.error("⚠️ Unable to connect to Google Sheets.")
    sheet = None

# --------------- QUESTION DEFINITION ---------------
questions = {
    "Q1": ("How regular was your menstrual cycle in the past year?", [
        "Does not apply (e.g., hormonal treatment or pregnancy)",
        "Regular (25–35 days)",
        "Often irregular (< 25 or > 35 days)",
        "Rarely got period (< 6 times a year)" ]),
    "Q2": ("Do you notice excessive thick black hair on your face, chest, or back?", [
        "No, not at all",
        "Yes, manageable with hair removal",
        "Yes, resistant to hair removal",
        "Yes + scalp thinning or hair loss" ]),
    "Q3": ("Have you had acne or oily skin this year?", [
        "No",
        "Yes, mild but manageable",
        "Yes, often despite treatment",
        "Yes, severe and persistent" ]),
    "Q4": ("Have you experienced weight changes?", [
        "No, stable weight",
        "Stable only with effort",
        "Struggling to maintain weight",
        "Can't lose weight despite diet/exercise" ]),
    "Q5": ("Do you feel tired or sleepy after meals?", [
        "No, not really",
        "Sometimes after heavy meals",
        "Yes, often regardless of food",
        "Yes, almost daily with alertness issues" ])
}

# --------------- UTILS ---------------
def get_country_choices():
    lst = []
    for c in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(c.alpha_2)
            flag = chr(127397 + ord(c.alpha_2[0])) + chr(127397 + ord(c.alpha_2[1]))
            lst.append(f"{flag} {c.name} (+{code})")
        except:
            pass
    return sorted(lst)

def validate_phone(country, num):
    try:
        dial = country.split("(+")[1].split(")")[0]
        pn = phonenumbers.parse(f"+{dial}{num}")
        return phonenumbers.is_valid_number(pn)
    except:
        return False

# --------------- INTRO PAGE ---------------
if st.session_state.step == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1‑minute quiz to understand your hormonal health — and how InBalance can help.")

    first = st.text_input("👩‍🦰 First Name")
    last = st.text_input("👩‍🦰 Last Name")
    email = st.text_input("📧 Email")
    country = st.selectbox("🌍 Country", get_country_choices())
    phone = st.text_input("📱 Phone (optional, no spaces)")

    if st.button("Start Quiz"):
        if not first.strip() or not last.strip() or not email.strip():
            st.warning("Please provide your name and email")
        elif phone and not validate_phone(country, phone):
            st.warning("Invalid phone number for that country")
        else:
            st.session_state.info = {
                "First Name": first, "Last Name": last,
                "Email": email, "Country": country, "Phone": phone
            }
            st.session_state.step = "quiz"
            st.rerun()

# --------------- QUIZ PAGE ---------------
elif st.session_state.step == "quiz":
    st.header("📝 Quick Quiz (answers optional)")
    for k, (q, opts) in questions.items():
        st.session_state.answers[k] = st.radio(q, opts, key=k, index=None)

    if st.button("Show Results & Continue"):
        st.session_state.step = "results"
        st.rerun()

# --------------- RESULTS PAGE ---------------
elif st.session_state.step == "results":
    answers = st.session_state.answers
    diag = "Mild Hormonal Imbalance"

    if answers.get("Q1","").lower().startswith(("often","rarely")):
        diag = "Cycle Irregularity"
    elif "resistant" in answers.get("Q2","") or "scalp" in answers.get("Q2",""):
        diag = "Potential PCOS"
    elif "can't lose" in answers.get("Q4","").lower():
        diag = "H‑PCO (Hormonal & Metabolic)"

    st.subheader(f"🧬 Diagnosis: {diag}")
    st.markdown("### 🔍 Personalized Recommendations:")

    recs = []
    if "often irregular" in answers.get("Q1","").lower():
        recs.append("Track cycles daily — a missed ovulation pattern can flag imbalance.")
    if "resistant" in answers.get("Q2","").lower():
        recs.append("Explore androgen reduction strategies — a specialist can guide you.")
    if "severe" in answers.get("Q3","").lower():
        recs.append("Targeted skincare + hormone review may improve persistent acne.")
    if "struggling" in answers.get("Q4","").lower():
        recs.append("Custom nutrition plans often help with metabolic weight resistance.")
    if "sleepy" in answers.get("Q5","").lower():
        recs.append("Balancing blood sugar post-meals can reduce fatigue — consider a plan.")

    for r in recs:
        st.info(r)

    st.warning("⚠️ Informational only — consult a physician before making health decisions.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 📅 Precision cycle & symptom tracking  
- 🧬 Phase-specific health tips  
- 🩺 Access to gynecologists, endocrinologists, nutritionists & trainers  
- 📊 Data-driven personalized plans  
- 🔁 Ongoing expert support as your body changes
""")
    st.image("qr_code.png", width=140)

    st.session_state.diagnosis = diag
    st.session_state.step = "waitlist"

# --------------- WAITLIST & SAVE ---------------
elif st.session_state.step == "waitlist":
    st.subheader("💬 Join our waitlist")
    join = st.radio("Would you like to join?", ["Yes", "No"], index=None)

    track = note = ""
    symptoms = []
    goal = ""

    if join == "Yes":
        track = st.radio("Do you track your cycles/symptoms?", [
            "Yes, with an app", "Yes, manually", "Not yet", "Other"], index=None)
        symptoms = st.multiselect("Your top symptoms:",[
            "Irregular cycles","Cravings","Low energy","Mood swings",
            "Bloating","Acne","Anxiety","Sleep issues","Brain fog"])
        goal = st.radio("Your main health goal:",[
            "Understand my cycle","Reduce symptoms","Get diagnosis",
            "Personalized plan","Just curious"], index=None)
        note = st.text_area("Anything else you'd like us to know?")

    if st.button("📩 Save & Finish"):
        row = [
            st.session_state.timestamp,
            *st.session_state.info.values(),
            *st.session_state.answers.values(),
            st.session_state.diagnosis,
            join, track,
            ", ".join(symptoms), goal, note
        ]
        try:
            if sheet:
                sheet.append_row(row)
                st.success("✅ Saved! You’re on our waitlist 🎉")
            else:
                st.error("⚠️ Could not save to sheet.")
        except Exception as e:
            st.error(f"⚠️ Save failed: {e}")

    if st.button("🔁 Restart"):
        st.session_state.clear()
        st.rerun()
