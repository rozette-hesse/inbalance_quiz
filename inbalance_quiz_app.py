import streamlit as st
from datetime import datetime
import re
import gspread
from PIL import Image
from google.oauth2.service_account import Credentials
import phonenumbers
import pycountry

# --- CONFIG ---
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# --- SESSION STATE INIT ---
if 'step' not in st.session_state:
    st.session_state.step = 'start'
    st.session_state.answers = []
    st.session_state.recs = []

# --- BUILD COUNTRY LIST ---
country_list = []
for country in pycountry.countries:
    try:
        code = phonenumbers.country_code_for_region(country.alpha_2)
        flag = chr(127397 + ord(country.alpha_2[0])) + chr(127397 + ord(country.alpha_2[1]))
        country_list.append((f"{flag} {country.name} (+{code})", f"+{code}", country.alpha_2))
    except:
        pass
country_list.sort(key=lambda x: x[0])

# --- GOOGLE SHEETS SETUP ---
try:
    cred = Credentials.from_service_account_info(st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"])
    sheet = gspread.authorize(cred).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# --- QUESTION LIST ---
questions = [
    ("How regular was your menstrual cycle in the past year?", [
        "Does not apply (e.g. pregnancy/hormonal treatment)",
        "Regular (25–35 days)",
        "Often irregular (<25 or >35 days)",
        "Rarely got period (<6 times a year)"
    ]),
    ("Do you notice excessive thick black hair on face, chest, or back?", [
        "No, not at all",
        "Yes, manageable with hair removal",
        "Yes, resistant to hair removal",
        "Yes + scalp thinning/hair loss"
    ]),
    ("Have you had acne or oily skin this year?", [
        "No", "Yes, mild but manageable",
        "Yes, often despite treatment",
        "Yes, severe and persistent"
    ]),
    ("Have you experienced weight changes?", [
        "No, stable weight",
        "Stable only with effort",
        "Struggling to maintain weight",
        "Can’t lose weight despite diet/exercise"
    ]),
    ("Do you feel tired or sleepy after meals?", [
        "No, not really",
        "Sometimes after heavy meals",
        "Yes, often regardless of food",
        "Yes, almost daily fatigue"
    ]),
]

# --- HELPER VALIDATION ---
def valid_email(e):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", e)
def valid_phone(code, num, region):
    try:
        p = phonenumbers.parse(code + num, region)
        return phonenumbers.is_valid_number(p)
    except:
        return False

# --- STEP: START ---
if st.session_state.step == 'start':
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A 1‑minute quiz to learn about your cycle, symptoms, and hormonal health.")

    fname = st.text_input("👩 First Name")
    lname = st.text_input("👩 Last Name")
    email = st.text_input("📧 Email Address")
    cpicker = st.selectbox("🌍 Country", [c[0] for c in country_list])
    idx = [c[0] for c in country_list].index(cpicker)
    code, region = country_list[idx][1], country_list[idx][2]
    phone = st.text_input("📱 Phone Number (no spaces)")
    
    if st.button("Start Quiz"):
        if not fname or not lname:
            st.warning("Enter your full name.")
        elif not valid_email(email):
            st.warning("Enter a valid email.")
        elif not phone.isdigit():
            st.warning("Phone must be numeric.")
        elif not valid_phone(code, phone, region):
            st.warning("Phone not valid for selected country.")
        else:
            st.session_state.user = [fname, lname, email, code + phone]
            st.session_state.step = 'quiz'
            st.rerun()

# --- STEP: QUIZ ---
elif st.session_state.step == 'quiz':
    st.header("📝 Answer All Questions")
    st.session_state.answers = []

    for i, (qtext, opts) in enumerate(questions):
        st.markdown(f"**{i+1}. {qtext}**")
        sel = st.radio("", opts, key=f"q{i}", index=None)
        st.session_state.answers.append(sel)

    if st.button("Submit"):
        if None in st.session_state.answers:
            st.warning("Answer all questions first.")
        else:
            st.session_state.step = 'results'
            st.rerun()

# --- STEP: RESULTS ---
elif st.session_state.step == 'results':
    st.success("✅ Quiz complete!")
    answers = st.session_state.answers
    recs = []

    # Diagnosis logic
    if any("irregular" in answers[i].lower() or "rarely" in answers[i].lower() for i in [0]):
        diag = "Cycle Irregularity"
    elif "resistant" in answers[1].lower() or "scalp thinning" in answers[1].lower():
        diag = "Androgen Excess"
    elif "persistent" in answers[2].lower():
        diag = "Hormonal Acne"
    elif "can't lose" in answers[3].lower():
        diag = "Metabolic Resistance"
    elif "almost daily fatigue" in answers[4].lower():
        diag = "Blood Sugar Imbalance"
    else:
        diag = "General Hormonal Fluctuations"

    st.markdown(f"### 🧬 Diagnosis: **{diag}**")

    # Per-answer recommendations
    st.markdown("### 🔧 Recommendations:")
    for i, ans in enumerate(answers):
        tip = ""
        if i == 0:
            tip = "- Track your cycle phase daily to identify hormonal patterns." if "irregular" in ans.lower() else "- Continue logging your cycle—your data is valuable."
        elif i == 1:
            tip = "- Hair changes? Discuss with experts about androgen tests & treatment."
        elif i == 2:
            tip = "- Acne? Our specialists can tailor treatment based on hormonal profile."
        elif i == 3:
            tip = "- Struggling with weight? We build metabolic-focused nutrition plans."
        elif i == 4:
            tip = "- Tired after meals? Learn how blood sugar phases connect with fatigue."
        st.info(tip)
    st.warning("**Disclaimer:** Informational only. Always consult your physician.")

    # InBalance support messaging
    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 📅 Precision cycle & symptom tracking across each phase  
- 🌡️ Symptom‑phase logic so recommendations align with where you are in your cycle  
- 🩺 Direct access to gynecologists, endocrinologists, nutritionists & trainers  
- 📊 Data‑driven insights for personalized lifestyle and clinical care  
- 🤝 Ongoing support to guide and adjust your journey
""")

    st.image("qr_code.png", width=160)
    st.session_state.step = 'waitlist'

# --- STEP: WAITLIST ---
elif st.session_state.step == 'waitlist':
    st.markdown("### 💬 Join our waitlist?")
    wl = st.radio("Interested in expert support?", ["Yes", "No"], index=None)

    if wl == "Yes":
        track = st.radio("… Do you track your cycle currently?", ["Yes, app", "Yes, manually", "No"])
        syms = st.multiselect("Which symptoms concern you?", ["Irregular cycles","Acne","Weight","Fatigue","Mood","Other"])
        goal = st.text_input("Your main health goal?")
        note = st.text_area("Anything else?")

    if st.button("📩 Finish & Save"):
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            *st.session_state.user,
            *answers,
            diag,
            wl,
            track if wl=="Yes" else "",
            ", ".join(syms) if wl=="Yes" else "",
            goal if wl=="Yes" else "",
            note if wl=="Yes" else ""
        ]
        try:
            sheet.append_row(row) if sheet else None
            st.success("✅ Saved! We'll reach out soon.")
        except:
            st.error("Could not save — internal error.")

    if st.button("🔄 Restart"):
        st.session_state.clear()
        st.rerun()
