import streamlit as st
from datetime import datetime
from PIL import Image
import re
import gspread
import phonenumbers
import pycountry
from google.oauth2.service_account import Credentials

# — CONFIG —
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# — SESSION STATE —
if 'step' not in st.session_state:
    st.session_state.step = 'start'
    st.session_state.answers = []
    st.session_state.user = []
    st.session_state.waitlist = None
    st.session_state.waitlist_details = {}

# — COUNTRY LIST (flags + codes) —
country_list = []
for country in pycountry.countries:
    try:
        code = phonenumbers.country_code_for_region(country.alpha_2)
        flag = chr(127397 + ord(country.alpha_2[0])) + chr(127397 + ord(country.alpha_2[1]))
        country_list.append((f"{flag} {country.name} (+{code})", f"+{code}", country.alpha_2))
    except:
        pass
country_list.sort(key=lambda x: x[0])

# — GOOGLE SHEETS SETUP —
try:
    cred = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    sheet = gspread.authorize(cred).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# — QUIZ QUESTIONS & OPTIONS —
questions = [
    ("How regular was your menstrual cycle in the past year?", 
        ["Does not apply (e.g. pregnancy/treatment)", "Regular (25–35 days)",
         "Often irregular (<25 or >35 days)", "Rarely got period (<6/year)"]),
    ("Do you notice excessive thick black hair on face/chest/back?", 
        ["No, not at all", "Yes, manageable with removal",
         "Yes, resistant to removal", "Yes + scalp thinning/hair loss"]),
    ("Have you had acne or oily skin this year?", 
        ["No", "Yes, mild", "Yes, often despite treatment", "Yes, severe"]),
    ("Have you experienced weight changes?", 
        ["No, stable", "Stable only with effort",
         "Struggling to maintain", "Can’t lose despite diet/exercise"]),
    ("Do you feel tired or sleepy after meals?", 
        ["No", "Sometimes", "Yes, often regardless of food", "Yes, daily fatigue"]),
]

# — VALIDATION HELPERS —
def valid_email(e):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", e)

def valid_phone(code, num, region):
    try:
        p = phonenumbers.parse(code + num, region)
        return phonenumbers.is_valid_number(p)
    except:
        return False

# — STEP: START —
if st.session_state.step == 'start':
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A quick quiz to guide you toward personalized hormonal support.")
    fname = st.text_input("👩 First Name")
    lname = st.text_input("👩 Last Name")
    email = st.text_input("📧 Email")
    cpicker = st.selectbox("🌍 Country", [c[0] for c in country_list])
    idx = [c[0] for c in country_list].index(cpicker)
    code, region = country_list[idx][1], country_list[idx][2]
    phone = st.text_input("📱 Phone Number (no spaces)")

    if st.button("Start Quiz"):
        if not fname or not lname:
            st.warning("Enter both first and last name.")
        elif not valid_email(email):
            st.warning("Enter a valid email address.")
        elif not phone.isdigit():
            st.warning("Phone must be numeric.")
        elif not valid_phone(code, phone, region):
            st.warning("Phone number doesn't match selected country.")
        else:
            st.session_state.user = [fname, lname, email, code + phone]
            st.session_state.step = 'quiz'
            st.rerun()

# — STEP: QUIZ —
elif st.session_state.step == 'quiz':
    st.header("📝 Answer All Questions")
    st.session_state.answers = []
    for i, (qtext, opts) in enumerate(questions):
        st.markdown(f"**{i+1}. {qtext}**")
        sel = st.radio("", opts, key=f"q{i}", index=None)
        st.session_state.answers.append(sel)
    if st.button("Submit"):
        if None in st.session_state.answers:
            st.warning("Answer all questions before submitting.")
        else:
            st.session_state.step = 'results'
            st.rerun()

# — STEP: RESULTS —
elif st.session_state.step == 'results':
    answers = st.session_state.answers
    st.success("✅ Quiz complete!")
    # Diagnosis
    if "irregular" in answers[0].lower() or "rarely" in answers[0].lower():
        diag = "Cycle Irregularity"
    elif "resistant" in answers[1].lower() or "scalp" in answers[1].lower():
        diag = "Androgen Excess"
    elif "severe" in answers[2].lower():
        diag = "Hormonal Acne"
    elif "can’t lose" in answers[3].lower():
        diag = "Metabolic Resistance"
    else:
        diag = "General Hormonal Fluctuations"
    st.markdown(f"### 🧬 Diagnosis: **{diag}**")

    # Personalized insights
    st.markdown("### 🔧 Recommendations based on your responses:")
    insights = {
        0: ["Track cycle phases daily to spot patterns."],
        1: ["Hair changes may signal androgen imbalance—consult specialists."],
        2: ["Oily/severe acne often ties to hormones—specialized care helps."],
        3: ["Difficulty losing weight? A metabolic plan can support you."],
        4: ["Fatigue after meals? Explore blood-sugar balancing strategies."]
    }
    for i, ans in enumerate(answers):
        st.info(insights[i][0])

    st.warning("⚠️ *Information only. Always consult your physician.*")

    # InBalance benefits
    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 📅 Precise cycle & symptom **phase tracking**  
- 🔄 Symptom-phase logic for **tailored guidance**  
- 🩺 Access to gynecologists, endocrinologists, nutritionists & personal trainers  
- 🧠 Data-driven plans for lifestyle & clinical care  
- 🤝 Ongoing support and adjustments as you progress
""")

    st.image("qr_code.png", width=160)
    st.session_state.step = 'waitlist'

# — STEP: WAITLIST —
elif st.session_state.step == 'waitlist':
    st.markdown("### 💬 Would you like to join our expert waitlist?")
    wl = st.radio("Interested?", ["Yes", "No"], index=None)
    st.session_state.waitlist = wl

    details = {}
    if wl == "Yes":
        details['track'] = st.radio("Track your cycle currently?", ["App", "Manually", "No"])
        details['symptoms'] = st.multiselect(
            "Which symptoms concern you?",
            ["Irregular cycles", "Acne", "Weight", "Fatigue", "Mood swings", "Other"]
        )
        details['goal'] = st.text_input("Your primary health goal")
        details['notes'] = st.text_area("Anything else you'd like us to know?")
        st.session_state.waitlist_details = details

    if st.button("📩 Finish & Save"):
        row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + st.session_state.user + answers + [diag, wl]
        if wl == "Yes":
            row += [details['track'], ", ".join(details['symptoms']), details['goal'], details['notes']]
        else:
            row += [""] * 4
        try:
            if sheet:
                sheet.append_row(row)
                st.success("✅ Your information has been saved. We’ll be in touch!")
            else:
                st.error("❌ Save failed — please try again later.")
        except:
            st.error("❌ Save error — internal issue.")

    if st.button("🔄 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
