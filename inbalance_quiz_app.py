import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# --------------- CONFIG ----------------
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# --------------- SESSION INIT ---------------
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.info = {}
    st.session_state.answers = {}
    st.session_state.diagnosis = ""
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --------------- GOOGLE SHEETS ---------------
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except Exception:
    sheet = None

# --------------- QUESTIONS ----------------
questions = {
    "Q1": ("How regular was your menstrual cycle in the past year?", [
        "Does not apply (e.g., hormonal treatment or pregnancy)",
        "Regular (25–35 days)",
        "Often irregular (< 25 or > 35 days)",
        "Rarely got period (< 6 times a year)"
    ]),
    "Q2": ("Do you notice excessive thick black hair on your face, chest, or back?", [
        "No, not at all",
        "Yes, manageable with hair removal",
        "Yes, resistant to hair removal",
        "Yes + scalp thinning or hair loss"
    ]),
    "Q3": ("Have you had acne or oily skin this year?", [
        "No",
        "Yes, mild but manageable",
        "Yes, often despite treatment",
        "Yes, severe and persistent"
    ]),
    "Q4": ("Have you experienced weight changes?", [
        "No, stable weight",
        "Stable only with effort",
        "Struggling to maintain weight",
        "Can't lose weight despite diet/exercise"
    ]),
    "Q5": ("Do you feel tired or sleepy after meals?", [
        "No, not really",
        "Sometimes after heavy meals",
        "Yes, often regardless of food",
        "Yes, almost daily with alertness issues"
    ])
}

# --------------- UTIL FUNCTIONS ---------------
def get_country_choices():
    choices = []
    for c in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(c.alpha_2)
            emoji = chr(127397 + ord(c.alpha_2[0])) + chr(127397 + ord(c.alpha_2[1]))
            choices.append(f"{emoji} {c.name} (+{code})")
        except:
            pass
    return sorted(set(choices))

def validate_phone(country_entry, number):
    try:
        country_code = country_entry.split("(+")[1].split(")")[0]
        phone_obj = phonenumbers.parse(f"+{country_code}{number}")
        return phonenumbers.is_valid_number(phone_obj)
    except:
        return False

# --------------- PAGE: INTRO ---------------
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1‑minute quiz to understand your hormonal health — and how InBalance can help.")
    fn = st.text_input("👩‍🦰 First Name")
    ln = st.text_input("👩‍🦰 Last Name")
    em = st.text_input("📧 Email")
    countries = get_country_choices()
    ct = st.selectbox("🌍 Country", [""] + countries)
    ph = st.text_input("📱 Phone (no spaces)")

    if st.button("Start Quiz"):
        if not all([fn.strip(), ln.strip(), em.strip(), ph.strip(), ct]):
            st.warning("Please complete all fields.")
        elif not validate_phone(ct, ph):
            st.warning("Invalid phone number for selected country.")
        else:
            st.session_state.info = {"First Name": fn, "Last Name": ln, "Email": em, "Country": ct, "Phone": ph}
            st.session_state.page = "quiz"
            st.rerun()
    st.stop()

# --------------- PAGE: QUIZ ---------------
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    for k, (qtext, opts) in questions.items():
        st.session_state.answers[k] = st.radio(f"**{qtext}**", opts, key=k)

    if st.button("Submit Answers"):
        if any(not ans for ans in st.session_state.answers.values()):
            st.warning("Please answer all questions.")
        else:
            st.session_state.page = "results"
            st.rerun()
    st.stop()

# --------------- PAGE: RESULTS ---------------
elif st.session_state.page == "results":
    st.header("🧬 Your Diagnosis & Personalized Insights")
    A = st.session_state.answers
    # Determine diagnosis
    if "irregular" in A["Q1"]:
        diag = "Cycle Irregularity"
    elif "resistant" in A["Q2"] or "scalp" in A["Q2"]:
        diag = "Potential PCOS"
    elif "Can't lose weight" in A["Q4"]:
        diag = "Hormonal + Metabolic Concerns"
    else:
        diag = "Mild Hormonal Imbalance"
    st.session_state.diagnosis = diag

    st.subheader(f"🧬 Diagnosis: {diag}")
    st.markdown("### 🔧 Targeted Recommendations:")
    recs = []
    if "irregular" in A["Q1"]:
        recs.append("Start daily cycle tracking—log basal temperature, flow, and symptoms to identify ovulation patterns.")
    if "resistant" in A["Q2"] or "scalp" in A["Q2"]:
        recs.append("Hair thickening or loss may signal elevated androgens—our endocrinologists can evaluate hormonal levels and treatment.")
    if "severe" in A["Q3"] or "oily" in A["Q3"]:
        recs.append("Persistent acne can be hormone-related—dermatologists and endocrinologists can tailor treatments.")
    if "Can't lose weight" in A["Q4"]:
        recs.append("Difficulty losing weight may be metabolic—consider a personalized nutrition and insulin-sensitivity plan.")
    if "sleepy" in A["Q5"] or "fatigue" in A["Q5"]:
        recs.append("Post-meal tiredness suggests glucose fluctuations; we offer blood sugar balancing strategies.")

    for r in recs:
        st.info(r)

    st.warning("⚠️ Informational only. Always consult a physician before making decisions.")
    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 📅 Cycle + symptom phase tracking gives deeper insight  
- 📊 Recommendations adapt to your current cycle and symptoms  
- 🩺 Direct access to gynecologists, endocrinologists, nutritionists & trainers  
- 📚 Personalized data‑backed lifestyle and treatment plans  
- 🔄 Ongoing support—experts adjust your journey as your body changes
    """)
    st.image("qr_code.png", width=140)

    # 🔁 Auto-save to Sheets here
    if sheet:
        try:
            sheet.append_row([
                st.session_state.timestamp,
                *st.session_state.info.values(),
                *st.session_state.answers.values(),
                st.session_state.diagnosis,
                "N/A", "", "", "", ""
            ])
        except Exception as e:
            st.error(f"Auto-save failed: {e}")

    if st.button("Continue to Waitlist"):
        st.session_state.page = "waitlist"
        st.experimental_rerun()
    st.stop()

# --------------- PAGE: WAITLIST ---------------
elif st.session_state.page == "waitlist":
    st.subheader("💬 Want to join the InBalance waitlist?")
    join = st.radio("Would you like to join?", ["Yes", "No"])
    track = ""
    symptoms = []
    goal = ""
    notes = ""
    if join == "Yes":
        track = st.radio("Do you track your cycle/symptoms?", ["Yes, with an app", "Yes, manually", "Not yet", "Other"])
        symptoms = st.multiselect("Top symptoms you face:", ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog"])
        goal = st.radio("Main health goal:", ["Understand my cycle", "Reduce symptoms", "Get diagnosis", "Personalized plan", "Just curious"])
        notes = st.text_area("Other notes you'd like to share:")

    if st.button("📩 Save & Finish"):
        if sheet:
            try:
                sheet.append_row([
                    st.session_state.timestamp,
                    *st.session_state.info.values(),
                    *st.session_state.answers.values(),
                    st.session_state.diagnosis,
                    join,
                    track,
                    ", ".join(symptoms),
                    goal,
                    notes
                ])
                st.success("✅ Your responses are saved — we’ll keep you updated!")
            except Exception as e:
                st.error(f"Error saving: {e}")
        else:
            st.error("❌ Could not connect to Google Sheets.")

    if st.button("🔁 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
