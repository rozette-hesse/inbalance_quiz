import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIG ---
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# --- SESSION INIT ---
if "stage" not in st.session_state:
    st.session_state.stage = "intro"
    st.session_state.info, st.session_state.answers = {}, {}
    st.session_state.diagnosis, st.session_state.recs = "", []
    st.session_state.saved = False

# --- SHEETS INIT ---
try:
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"])
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# --- QUESTIONS ---
questions = [
    ("How regular was your menstrual cycle in the past year?", [
        "Does not apply (e.g., hormonal treatment or pregnancy)",
        "Regular (25–35 days)",
        "Often irregular (< 25 or > 35 days)",
        "Rarely got period (< 6 times a year)"
    ]),
    ("Do you notice excessive thick black hair on your face, chest, or back?", [
        "No, not at all",
        "Yes, manageable with hair removal",
        "Yes, resistant to hair removal",
        "Yes + scalp thinning or hair loss"
    ]),
    ("Have you had acne or oily skin this year?", [
        "No",
        "Yes, mild but manageable",
        "Yes, often despite treatment",
        "Yes, severe and persistent"
    ]),
    ("Have you experienced weight changes?", [
        "No, stable weight",
        "Stable only with effort",
        "Struggling to maintain weight",
        "Can't lose weight despite diet/exercise"
    ]),
    ("Do you feel tired or sleepy after meals?", [
        "No, not really",
        "Sometimes after heavy meals",
        "Yes, often regardless of food",
        "Yes, almost daily with alertness issues"
    ]),
]

# --- UTIL FUNCTIONS ---
def get_countries():
    choices = []
    for c in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(c.alpha_2)
            emoji = chr(127397 + ord(c.alpha_2[0])) + chr(127397 + ord(c.alpha_2[1]))
            choices.append(f"{emoji} {c.name} (+{code})")
        except:
            pass
    return sorted(choices)

def validate_phone(country_str, number):
    try:
        code = country_str.split("(+")[1].split(")")[0]
        pn = phonenumbers.parse(f"+{code}{number}")
        return phonenumbers.is_valid_number(pn)
    except:
        return False

# --- INTRO ---
if st.session_state.stage == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1‑minute quiz to understand your hormonal health.")

    fn = st.text_input("👩‍🦰 First Name", "")
    ln = st.text_input("👩‍🦰 Last Name", "")
    em = st.text_input("📧 Email", "")
    country = st.selectbox("🌍 Country", [""] + get_countries())
    ph = st.text_input("📱 Phone (no spaces)", "")

    if st.button("Start Quiz"):
        if not all([fn, ln, em, country, ph]):
            st.warning("All fields are required.")
        elif not validate_phone(country, ph):
            st.warning("Invalid phone for selected country.")
        else:
            st.session_state.info = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                     "First Name": fn, "Last Name": ln,
                                     "Email": em, "Country": country, "Phone": ph}
            st.session_state.stage = "quiz"
            st.rerun()
    st.stop()

# --- QUIZ ---
if st.session_state.stage == "quiz":
    st.header("📝 Answer All Questions")
    for idx, (text, opts) in enumerate(questions, 1):
        st.session_state.answers[f"Q{idx}"] = st.radio(text, opts, key=f"q{idx}", index=-1)

    if st.button("Submit"):
        if "" in st.session_state.answers.values():
            st.warning("Please answer all questions.")
        else:
            st.session_state.stage = "results"
            st.rerun()
    st.stop()

# --- RESULTS ---
if st.session_state.stage == "results":
    A = st.session_state.answers
    diag = "Mild Hormonal Imbalance"
    recs = []

    if "irregular" in A["Q1"]:
        diag = "Cycle Irregularity"
        recs.append("Track basal body temperature & flow daily. This can reveal ovulation patterns we can support.")
    if any(x in A["Q2"] for x in ["resistant", "scalp"]):
        diag = "Potential PCOS"
        recs.append("Hair changes may signal excess androgens — our endocrinologists can guide hormone testing & treatment.")
    if any(x in A["Q3"] for x in ["oily", "persistent", "severe"]):
        recs.append("Severe acne may be hormone-driven — targeted dermatological and hormonal care is available.")
    if "Can't lose weight" in A["Q4"]:
        diag = "Hormonal + Metabolic Concerns"
        recs.append("Difficulty losing weight suggests insulin resistance. A personalized metabolic plan helps.")
    if any(x in A["Q5"] for x in ["fatigue", "sleepy"]):
        recs.append("Feeling tired post-meals? We offer blood-sugar balancing strategies to help your energy.")

    st.subheader(f"🧬 Diagnosis: {diag}")
    st.markdown("### 🔧 Personalized Recommendations:")
    for r in recs:
        st.info(r)
    st.warning("⚠️ Informational only. Consult your physician.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 📅 Cycle + symptom phase tracking  
- 📊 Phase‑specific health recommendations  
- 🩺 Access to gynecologists, endocrinologists, nutritionists & trainers  
- 📚 Personalized data‑driven plans  
- 🔄 Ongoing expert-led guidance
    """)
    st.image("qr_code.png", width=140)

    st.session_state.diagnosis = diag
    st.session_state.recs = recs

    if sheet and not st.session_state.saved:
        row = list(st.session_state.info.values()) + list(A.values()) + [diag, "N/A","", "", "", ""]
        sheet.append_row(row)
        st.session_state.saved = True

    if st.button("Join Waitlist"):
        st.session_state.stage = "waitlist"
        st.rerun()
    st.stop()

# --- WAITLIST ---
if st.session_state.stage == "waitlist":
    st.header("💬 Join the InBalance Waitlist")

    join = st.radio("Would you like to join?", ["Yes", "No"], index=0)
    track = symptoms = goal = notes = ""

    if join == "Yes":
        track = st.radio("Track cycle/symptoms?", ["Yes, with an app", "Yes, manually", "Not yet", "Other"])
        symptoms = st.multiselect("Top symptoms:", ["Irregular cycles", "Cravings", "Low energy",
                                                     "Mood swings", "Bloating", "Acne",
                                                     "Anxiety", "Sleep issues", "Brain fog"])
        goal = st.radio("Main goal:", ["Understand cycle", "Reduce symptoms",
                                       "Get diagnosis", "Personalized plan", "Just curious"])
        notes = st.text_area("Other notes:")

    if st.button("Save & Finish"):
        if sheet:
            row = list(st.session_state.info.values()) + list(st.session_state.answers.values()) + \
                  [st.session_state.diagnosis, join, track, ", ".join(symptoms), goal, notes]
            try:
                sheet.append_row(row)
                st.success("✅ Saved! We’ll be in touch.")
            except Exception as e:
                st.error(f"Error saving: {e}")
        st.session_state.stage = "done"
        st.stop()

    st.stop()

if st.session_state.stage == "done":
    st.success("🎉 Thank you! Your quiz and waitlist info have been recorded.")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
