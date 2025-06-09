import streamlit as st
from PIL import Image
import re, unicodedata
import pycountry
import phonenumbers
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# — CONFIG —
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# — SESSION INIT —
for key, val in {
    "step": 0,
    "answers": {},
    "first": "", "last": "", "email": "", "country": "", "phone": "",
    "waitlist": None, "tracking": "", "symptoms": [], "goal": "", "notes": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# — GOOGLE SHEETS AUTH —
try:
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except Exception:
    sheet = None

# — UTILS —
def flag_emoji(cc):
    return "".join(unicodedata.lookup(f"REGIONAL INDICATOR SYMBOL LETTER {c}") for c in cc)

def valid_phone(cc, num):
    try:
        pn = phonenumbers.parse(num, cc)
        return phonenumbers.is_valid_number(pn)
    except:
        return False

# — QUESTIONS & OPTIONS —
qs = {
    1: "How regular was your menstrual cycle in the past year?",
    2: "Do you notice excessive thick black hair on your face, chest, or back?",
    3: "Have you had acne or oily skin this year?",
    4: "Have you experienced weight changes?",
    5: "Do you feel tired or sleepy after meals?"
}
opts = {
    1: ["Does not apply", "Regular (25–35d)", "Often irregular", "Rarely got period"],
    2: ["No, not at all", "Yes, manageable", "Yes, resistant", "Yes + thinning"],
    3: ["No", "Yes, mild", "Yes, frequent", "Yes, severe"],
    4: ["No change", "Stable with effort", "Struggling", "Can't lose"],
    5: ["No", "Sometimes", "Often", "Almost daily"]
}

# — STEP 0: PERSONAL INFO —
if st.session_state.step == 0:
    st.title("How Balanced Are Your Hormones?")
    st.text_input("🙋‍♀️ First Name", key="first")
    st.text_input("🙋‍♀️ Last Name", key="last")
    st.text_input("✉️ Email Address", key="email")

    countries = sorted(pycountry.countries, key=lambda c: c.name)
    formatted = [f"{flag_emoji(c.alpha_2)} {c.name} (+{phonenumbers.country_code_for_region(c.alpha_2)})" for c in countries]
    choice = st.selectbox("🌍 Country", [""] + formatted)
    if choice:
        st.session_state.country = countries[formatted.index(choice)].alpha_2

    st.text_input("📱 Phone (no spaces)", key="phone")

    if st.button("Start Quiz"):
        if not all([st.session_state.first, st.session_state.last, st.session_state.email, st.session_state.country, st.session_state.phone]):
            st.warning("All fields are required.")
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", st.session_state.email):
            st.warning("Invalid email.")
        elif not valid_phone(st.session_state.country, st.session_state.phone):
            st.warning("Invalid phone number.")
        else:
            st.session_state.step = 1
            st.rerun()

# — STEP 1: QUIZ —
elif st.session_state.step == 1:
    st.header("📝 Answer All Questions")
    for i, q in qs.items():
        st.markdown(f"**{i}. {q}**")
        st.session_state.answers[i] = st.radio("", opts[i], key=f"q{i}")
        st.markdown("---")
    if st.button("See Results"):
        if any(ans == "" for ans in st.session_state.answers.values()):
            st.warning("Please answer all.")
        else:
            st.session_state.step = 2
            st.rerun()

# — STEP 2: RESULTS + WAITLIST —
elif st.session_state.step == 2:
    score = sum(opts[i].index(st.session_state.answers[i]) for i in qs)
    if score < 5:
        diag = "No strong hormonal imbalance"
    elif score < 10:
        diag = "Ovulatory Imbalance"
    elif score < 15:
        diag = "Potential PCOS"
    else:
        diag = "Androgenic + Metabolic Imbalance"

    st.markdown(f"### 🧬 Diagnosis: {diag}")
    st.success("✅ Quiz complete!")

    # personalized recs
    rec = []
    a = st.session_state.answers
    rec.append("• Irregular or missed periods → daily cycle-phase tracking paired with LH/basal body temperature can help.")
    if a[2] != opts[2][0]:
        rec.append("• Excess facial or chest hair may indicate androgen sensitivity. Discuss with an endocrinologist.")
    if a[3] != opts[3][0]:
        rec.append("• Acne severity suggests hormonal inflammation—dermatologist or hormonal therapy may help.")
    if a[4] != opts[4][0]:
        rec.append("• Weight changes may be metabolic. A lifestyle plan with nutritional coaching could support you.")
    if a[5] != opts[5][0]:
        rec.append("• Fatigue after meals hints at blood sugar imbalance—tailored nutrition/phases analysis can help.")

    for r in rec:
        st.info(r)

    st.warning("⚠️ Informational only. Always consult your physician.")

    st.markdown("---")
    st.markdown("💡 **Why InBalance Helps**")
    st.markdown("""
    • 📆 Precise cycle & symptom **phase tracking**  
    • 🧠 Symptom-phase logic for tailored daily insights  
    • 🩺 Access to gynecologists, endocrinologists, nutritionists & trainers  
    • 📊 Data-driven care plans adapted to YOU  
    • 🧡 Ongoing monitoring and clinical support  
    """)

    st.image("qr_code.png", width=180)
    st.markdown("---")
    st.markdown("### 💬 Join the InBalance Waitlist")
    st.session_state.waitlist = st.radio("Would you like to join?", ["Yes", "No"])
    if st.session_state.waitlist == "Yes":
        st.session_state.tracking = st.radio("Track cycle/symptoms by:", ["App","Manual","Not yet","Unsure"])
        st.session_state.symptoms = st.multiselect("Main symptoms:", ["Irregular cycle","Cravings","Low energy","Mood swings","Bloating","Acne","Anxiety","Sleep issues","Brain fog","Other"])
        st.session_state.goal = st.radio("Health Goal:", ["Understand cycle","Reduce symptoms","Get diagnosis","Personalized plan","Just curious","Other"])
        st.session_state.notes = st.text_area("Anything else?")

    if st.button("📩 Finish & Save"):
        if sheet:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                st.session_state.first,
                st.session_state.last,
                st.session_state.email,
                st.session_state.country,
                st.session_state.phone,
                diag
            ]
            row += [st.session_state.answers[i] for i in qs]
            row += [st.session_state.waitlist, st.session_state.tracking, ", ".join(st.session_state.symptoms), st.session_state.goal, st.session_state.notes]
            sheet.append_row(row)
            st.success("✅ Responses saved. We'll contact you soon!")
        else:
            st.error("❌ Can't save—Sheet not connected.")
        st.session_state.step = 3

# — STEP 3: THANK YOU —
elif st.session_state.step == 3:
    st.balloons()
    st.write("Thank you! We'll be in touch soon 😊")
    if st.button("🔄 Restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
