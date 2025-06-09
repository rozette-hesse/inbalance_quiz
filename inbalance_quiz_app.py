import streamlit as st
from PIL import Image
import re
import gspread
from google.oauth2.service_account import Credentials
import phonenumbers
from datetime import datetime
import pycountry

# --- CONFIG ---
st.set_page_config(page_title="InBalance Hormonal Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# --- SESSION STATE INIT ---
if "step" not in st.session_state:
    st.session_state.step = "start"  # start ➜ quiz ➜ results
for field in ("first", "last", "email", "country", "phone"):
    if field not in st.session_state:
        st.session_state[field] = ""
if "answers" not in st.session_state:
    st.session_state.answers = {}
for field in ("waitlist", "tracking", "symptoms", "goal", "notes"):
    if field not in st.session_state:
        st.session_state[field] = ""

# --- GSheets ---
try:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ],
    )
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except Exception:
    sheet = None

# --- QUESTIONS & OPTIONS ---
questions = [
    ("How regular was your menstrual cycle in the past year?", ["Does not apply", "Regular", "Often irregular", "Rarely got period"]),
    ("Do you notice excessive thick black hair on your face, chest, or back?", ["No, not at all", "Yes manageable", "Yes resistant", "Yes + scalp thinning"]),
    ("Have you had acne or oily skin this year?", ["No", "Yes mild", "Yes often", "Yes severe"]),
    ("Have you experienced weight changes?", ["Stable", "Stable w/ effort", "Struggling", "Can't lose weight"]),
    ("Do you feel tired or sleepy after meals?", ["No", "Sometimes", "Yes often", "Yes almost daily"]),
]

# --- START PAGE ---
if st.session_state.step == "start":
    st.title("How Balanced Are Your Hormones?")
    st.text_input("👩‍⚕️ First Name", key="first")
    st.text_input("👩‍⚕️ Last Name", key="last")
    st.text_input("📧 Email", key="email")

    countries = sorted([ (f"{c.flag} {c.name} (+{c.country_code})", c.alpha_2, c.country_code)
                        for c in pycountry.countries if hasattr(c, "country_code") ],
                       key=lambda x: x[0])
    sel = st.selectbox("🌍 Country", [""] + [c[0] for c in countries])
    st.session_state.country = next((country[1] for country in countries if country[0] == sel), "")

    st.text_input("📱 Phone (no spaces)", key="phone")

    if st.button("Start Quiz"):
        if not st.session_state.first.strip() or not st.session_state.last.strip():
            st.warning("Please enter full name.")
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", st.session_state.email):
            st.warning("Enter valid email.")
        elif not st.session_state.country:
            st.warning("Select a country.")
        else:
            try:
                num = phonenumbers.parse(st.session_state.phone, st.session_state.country)
                if not phonenumbers.is_valid_number(num):
                    st.warning("Invalid phone for country.")
                    st.stop()
            except:
                st.warning("Invalid phone or format.")
                st.stop()

            st.session_state.step = "quiz"
            st.rerun()

# --- QUIZ PAGE ---
elif st.session_state.step == "quiz":
    st.header("📝 Answer All Questions")
    for idx, (q, opts) in enumerate(questions, 1):
        st.write(f"**{idx}. {q}**")
        key = f"q{idx}"
        if key not in st.session_state.answers:
            st.session_state.answers[key] = ""
        st.session_state.answers[key] = st.radio("", opts, key=key, index=-1)

    if st.button("Submit Answers"):
        if any(v == "" for v in st.session_state.answers.values()):
            st.warning("Please answer all questions.")
        else:
            st.session_state.step = "results"
            st.rerun()

# --- RESULTS + WAITLIST ---
else:
    # DIAGNOSIS
    score_map = {
        "Does not apply":0, "Regular":1, "Often irregular":6, "Rarely got period":8,
        "No, not at all":1, "Yes manageable":5, "Yes resistant":7, "Yes + scalp thinning":8,
        "No":1, "Yes mild":4, "Yes often":6, "Yes severe":8,
        "Stable":1, "Stable w/ effort":2, "Struggling":5, "Can't lose weight":7,
        "No":1, "Sometimes":2, "Yes often":4, "Yes almost daily":6
    }
    total = sum(score_map.get(v,0) for v in st.session_state.answers.values())

    if total < 8:
        dx = "Balanced"
        insights = ["You appear to have balanced hormonal function."]
    elif total < 16:
        dx = "Ovulatory Imbalance"
        insights = ["Tracking ovulation may help clarify patterns."]
    elif total < 24:
        dx = "Possible PCOS"
        insights = ["Symptoms fit mild PCOS — symptom tracking is key."]
    else:
        dx = "Androgenic + Metabolic signs"
        insights = ["Symptoms suggest metabolic + androgen imbalance — see specialists."]

    st.markdown(f"### 🧬 Diagnosis: **{dx}**")
    st.markdown("#### 🔍 Personalized Recommendations:")
    recs = {
        1:"Cycle irregularity—track phases daily for insight.",
        2:"Hair growth—see an endocrinologist or dermatologist.",
        3:"Oily/severe acne—consider hormone-friendly skin care & nutrition.",
        4:"Weight difficulty—metabolic nutrition & exercise plans help.",
        5:"Post-meal fatigue—try balanced carbs/protein for blood sugar."
    }
    for i in range(1,6):
        st.info(recs[i])

    st.warning("⚠️ Informational only. Always consult a physician.")

    st.success("💡 Why InBalance Helps")
    st.markdown("""
        • **Cycle & symptom phase tracking** to identify patterns.  
        • **Symptom-phase intelligence** — e.g., PMS fatigue or mid-cycle acne.  
        • **Expert team access**: gynecologists, endocrinologists, nutritionists, trainers.  
        • **Data‑driven lifestyle & clinical plans** tailored to you.  
        • **Ongoing support** — adapt as you grow and progress.
    """)

    st.image("qr_code.png", width=180)

    st.markdown("### ✍️ Join the InBalance Waitlist")
    st.session_state.waitlist = st.radio("Would you like to join?", ["Yes","No"], index=-1)
    if st.session_state.waitlist == "Yes":
        st.session_state.tracking = st.radio("How do you currently track?", ["App","Manual","Not yet","Unsure"], index=-1)
        st.session_state.symptoms = st.multiselect("Select your main symptoms:", [
            "Irregular cycles","Cravings","Low energy","Mood swings",
            "Bloating","Acne","Anxiety","Sleep issues","Brain fog","Other"
        ])
        st.session_state.goal = st.radio("What's your main health goal?", [
            "Understand cycle","Reduce symptoms","Get diagnosis",
            "Lifestyle plan","Curious"], index=-1)
        st.session_state.notes = st.text_area("Anything else you'd like to add?")

    if st.button("📩 Finish & Save"):
        try:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                st.session_state.first,
                st.session_state.last,
                st.session_state.email,
                st.session_state.country + st.session_state.phone,
                dx
            ]
            for i in range(1,6):
                row.append(st.session_state.answers[f"q{i}"])
            row += [st.session_state.waitlist, st.session_state.tracking, ", ".join(st.session_state.symptoms),
                    st.session_state.goal, st.session_state.notes]
            if sheet: sheet.append_row(row)
            st.success("✅ All info saved!")
        except Exception as e:
            st.error(f"Save error: {e}")

    if st.button("🔄 Restart"):
        for field in ("step","first","last","email","country","phone","answers","waitlist","tracking","symptoms","goal","notes"):
            st.session_state[field] = {} if field=="answers" else ""
        st.session_state.step = "start"
        st.rerun()
