import streamlit as st
from PIL import Image
import re
import gspread
from google.oauth2.service_account import Credentials
import phonenumbers
from datetime import datetime
import pycountry

# --- CONFIG ---
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# --- SESSION INIT ---
defaults = {
    "first_name": "", "last_name": "", "email": "",
    "country": None, "phone": "",
    "answers": {},
    "submitted": False,
    "waitlist": None, "tracking": "", "symptoms": [], "goal": "", "notes": ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- G-SHEETS SETUP ---
try:
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except Exception:
    sheet = None

# --- FORM ---
if not st.session_state.submitted:
    st.title("How Balanced Are Your Hormones?")
    st.text_input("👩‍⚕️ First Name:", key="first_name")
    st.text_input("👩‍⚕️ Last Name:", key="last_name")
    st.text_input("📧 Email Address:", key="email")

    # Full country dropdown with flags
    country_list = sorted([
        (f"{country.flag} {country.name} (+{country.country_code})", country.alpha_2)
        for country in pycountry.countries if hasattr(country, "country_code")
    ], key=lambda x: x[0])
    sel = st.selectbox("🌐 Country:", [""] + [c[0] for c in country_list])
    st.session_state.country = next((c[1] for c in country_list if c[0] == sel), None)
    st.text_input("📱 Phone number (no spaces, local number):", key="phone")

    questions = {
        1: "How regular was your menstrual cycle in the past year?",
        2: "Do you notice excessive thick black hair on your face, chest, or back?",
        3: "Have you had acne or oily skin this year?",
        4: "Have you experienced weight changes?",
        5: "Do you feel tired/sleepy after meals?"
    }
    options = {
        1: ["Does not apply", "Regular", "Often irregular", "Rarely got period"],
        2: ["No, not at all", "Yes, manageable", "Yes, resistant", "Yes + scalp thinning"],
        3: ["No", "Yes, mild", "Yes, often", "Yes, severe"],
        4: ["Stable", "Stable w/ effort", "Struggling", "Can't lose weight"],
        5: ["No", "Sometimes", "Yes often", "Yes almost daily"]
    }
    st.markdown("### 📝 Answer All Questions")
    for q, text in questions.items():
        st.markdown(f"**{q}. {text}**")
        st.session_state.answers[str(q)] = st.radio("", options[q], key=f"q{q}", index=None)

    if st.button("Start Quiz"):
        # Validate
        if not st.session_state.first_name.strip() or not st.session_state.last_name.strip():
            st.warning("Please enter both names.")
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", st.session_state.email):
            st.warning("Enter a valid email.")
        elif not st.session_state.country:
            st.warning("Select country.")
        else:
            try:
                parsed = phonenumbers.parse(st.session_state.phone, st.session_state.country)
                if not phonenumbers.is_valid_number(parsed):
                    st.warning("Invalid phone for selected country.")
                    raise ValueError
            except:
                st.stop()
            for q in questions:
                if not st.session_state.answers.get(str(q)):
                    st.warning("Answer all questions.")
                    st.stop()
            st.session_state.submitted = True
            st.rerun()

# --- RESULTS + RECOMMENDATIONS ---
if st.session_state.submitted:
    # Diagnosis mapping
    scoremap = {
        "Does not apply": 0, "Regular": 1, "Often irregular": 6, "Rarely got period": 8,
        "No, not at all": 1, "Yes, manageable": 5, "Yes, resistant": 7, "Yes + scalp thinning": 8,
        "No": 1, "Yes, mild": 4, "Yes, often": 6, "Yes, severe": 8,
        "Stable": 1, "Stable w/ effort": 2, "Struggling": 5, "Can't lose weight": 7,
        "No": 1, "Sometimes": 2, "Yes often": 4, "Yes almost daily": 6
    }
    total = sum(scoremap.get(val, 0) for val in st.session_state.answers.values())
    if total < 8:
        dx = "Balanced"
        insights = ["Your cycle and symptoms seem in a healthy range."]
    elif total < 16:
        dx = "Ovulatory Imbalance"
        insights = [
            "Irregular ovulation may be contributing to fatigue or skin changes.",
            "Logging cycle phases can help identify luteal patterns."
        ]
    elif total < 24:
        dx = "Possible PCOS (HCA-PCO)"
        insights = [
            "Elevated hormone symptoms suggest potential PCOS.",
            "Tracking symptoms over months is essential for diagnosis."
        ]
    else:
        dx = "Androgen & Metabolic Signs (H-PCO)"
        insights = [
            "Your responses suggest both androgenic and metabolic imbalance.",
            "Consultation for insulin resistance and androgens recommended."
        ]

    st.markdown(f"### 🧬 Diagnosis: {dx}")
    st.markdown("### 🔧 Recommendations based on your responses:")
    rec_map = {
        1: "Cycle seems irregular—spot patterns to guide ovulation tracking.",
        2: "Hair changes suggest androgen activity—consider dermatological support.",
        3: "Oily/severe acne often correlates with hormones—diet & supplements may help.",
        4: "Difficulty losing weight—tailored metabolic plan advised.",
        5: "Post-meal fatigue hints at blood sugar dips—balanced snacks help."
    }
    for q, val in st.session_state.answers.items():
        st.info(rec_map[int(q)])

    st.warning("⚠️ Informational only. Always consult your physician.")

    # InBalance value section
    st.success("💡 Why InBalance Helps")
    st.markdown("""
        • **Precise cycle & symptom phase tracking** — understand exactly where your body is.<br>
        • **Symptom-phase logic** — insights tied to your cycle (e.g., PMS fatigue, mid-cycle breakouts).<br>
        • **Direct access to gynecologists, endocrinologists, nutritionists, and trainers** — comprehensive expert care.<br>
        • **Data-driven insights** — our team uses your history to tailor care.<br>
        • **Ongoing support & adjustments** — ensuring your journey evolves with you.
    """, unsafe_allow_html=True)
    st.image("qr_code.png", width=180)

    # Waitlist form
    st.markdown("### 💬 Join the InBalance Waitlist")
    st.session_state.waitlist = st.radio("Would you like to join?", ["Yes", "No"], index=None)
    if st.session_state.waitlist == "Yes":
        st.session_state.tracking = st.radio("How do you currently track symptoms?", ["App", "Manual", "Not yet", "Not sure"], index=None)
        st.session_state.symptoms = st.multiselect("Top symptoms you experience:", ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"])
        st.session_state.goal = st.radio("Your main health goal:", ["Understand cycle", "Reduce symptoms", "Get diagnosis", "Lifestyle plan", "Curious"], index=None)
        st.session_state.notes = st.text_area("Anything more you'd like to share?")

    # Save
    if st.button("📩 Finish & Save"):
        try:
            if sheet:
                data = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    st.session_state.first_name,
                    st.session_state.last_name,
                    st.session_state.email,
                    st.session_state.country + st.session_state.phone,
                    dx
                ]
                data += [st.session_state.answers[str(i)] for i in range(1, 6)]
                data += [st.session_state.waitlist,
                         st.session_state.tracking,
                         ", ".join(st.session_state.symptoms),
                         st.session_state.goal,
                         st.session_state.notes]
                sheet.append_row(data)
                st.success("✅ Saved! We'll be in touch.")
            else:
                st.error("❌ Google Sheets not connected.")
        except Exception as e:
            st.error(f"❌ Save error: {e}")

    if st.button("🔄 Restart Quiz"):
        st.session_state.update(defaults)
        st.rerun()
