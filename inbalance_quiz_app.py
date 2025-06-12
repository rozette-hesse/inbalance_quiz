import streamlit as st
from datetime import datetime
from PIL import Image
import phonenumbers
import pycountry
import gspread
from google.oauth2.service_account import Credentials

# ─── CONFIG ───────────────────────────────────────────────────
st.set_page_config("InBalance Hormonal Quiz", layout="centered")
logo = Image.open("logo.png")
st.image(logo, width=120)

# ─── SESSION INIT ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.answers = {}
    st.session_state.info = {}
    st.session_state.saved_quiz = False
    st.session_state.saved_waitlist = False
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ─── GOOGLE SHEETS SETUP ──────────────────────────────────────
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# ─── QUIZ DATA ─────────────────────────────────────────────────
questions = {
    "Q1": ("How regular was your menstrual cycle in the past year?", [
        "Does not apply (e.g., pregnancy or hormonal treatment)",
        "Regular (25–35 days)",
        "Often irregular (<25 or >35 days)",
        "Rarely got period (<6 times/year)"
    ]),
    "Q2": ("Do you notice thick black hair on your face, chest, or back?", [
        "No",
        "Yes, manageable",
        "Yes, resistant to removal",
        "Yes + scalp thinning/hair loss"
    ]),
    "Q3": ("Did you have acne or oily skin this year?", [
        "No",
        "Yes, mild",
        "Yes, frequent despite treatment",
        "Yes, severe/persistent"
    ]),
    "Q4": ("Have you experienced weight challenges?", [
        "No, weight is stable",
        "Weight stable only with effort",
        "Struggling to maintain weight",
        "Can't lose weight with diet/exercise"
    ]),
    "Q5": ("Do you feel tired after meals?", [
        "No",
        "Sometimes",
        "Yes, frequently",
        "Yes, daily with drowsiness"
    ]),
}

# ─── UTILITIES ─────────────────────────────────────────────────
def get_country_choices():
    items = []
    for c in pycountry.countries:
        try:
            cc = phonenumbers.country_code_for_region(c.alpha_2)
            emoji = chr(127397 + ord(c.alpha_2[0])) + chr(127397 + ord(c.alpha_2[1]))
            items.append(f"{emoji} {c.name} (+{cc})")
        except:
            continue
    return [""] + sorted(set(items))

def validate_phone(country, num):
    if not country or not num:
        return True
    try:
        cc = country.split("(+")[1].split(")")[0]
        p = phonenumbers.parse(f"+{cc}{num}")
        return phonenumbers.is_valid_number(p)
    except:
        return False

# ─── INTRO PAGE ──────────────────────────────────────────────
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A quick quiz to assess your hormonal health & see how InBalance can support you.")

    fn = st.text_input("First Name")
    ln = st.text_input("Last Name")
    email = st.text_input("Email")
    country = st.selectbox("Country (optional)", get_country_choices(), index=0)
    phone = st.text_input("Phone (no spaces, optional)")

    if st.button("Start Quiz"):
        if not fn.strip() or not ln.strip() or not email.strip():
            st.warning("Please fill in your name and email.")
        elif not validate_phone(country, phone):
            st.warning("Invalid phone number for the selected country.")
        else:
            st.session_state.info = {
                "First Name": fn,
                "Last Name": ln,
                "Email": email,
                "Country": country,
                "Phone": phone
            }
            st.session_state.page = "quiz"
            st.rerun()

# ─── QUIZ PAGE ───────────────────────────────────────────────
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    st.markdown("<hr>", unsafe_allow_html=True)

    for key, (text, options) in questions.items():
        st.markdown(f"**{text}**")
        sel = st.radio("", options, key=key, index=None)
        st.session_state.answers[key] = sel
        st.markdown("")  # spacing
        st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("Submit Answers"):
        if any(not v for v in st.session_state.answers.values()):
            st.warning("Please answer all questions.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ─── RESULTS + WAITLIST PAGE ─────────────────────────────────
elif st.session_state.page == "results":
    q = st.session_state.answers
    diagnosis = "Mild Hormonal Imbalance"
    recs = []

    if "irregular" in q["Q1"].lower() or "rarely" in q["Q1"].lower():
        diagnosis = "Cycle Irregularity"
        recs.append("📅 Start daily cycle tracking (e.g. basal temperature & symptoms) to identify ovulation patterns.")
    if "resistant" in q["Q2"].lower() or "scalp" in q["Q2"].lower():
        diagnosis = "Potential PCOS"
        recs.append("🩺 Consider an androgen panel and discuss hair changes with an endocrinologist.")
    if "frequent" in q["Q3"].lower() or "persistent" in q["Q3"].lower():
        recs.append("💆‍♀️ Explore a personalized skincare routine paired with hormonal assessment.")
    if "struggling" in q["Q4"].lower() or "can't" in q["Q4"].lower():
        diagnosis = "H-PCO (Hormonal & Metabolic)"
        recs.append("🍏 A structured nutrition and fitness plan can help support weight balance.")
    if "yes" in q["Q5"].lower():
        recs.append("🥗 Include protein and fiber at meals to reduce post-meal fatigue.")

    st.subheader(f"🧬 Diagnosis: {diagnosis}")
    st.markdown("### Recommendations based on your answers:")
    for r in recs:
        st.info(r)
    st.warning("⚠️ INFORMATIONAL ONLY — always consult your physician before making any actions.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 **Accurate cycle & symptom tracking**  
- 🩺 **Expert support** (gynecologists, endocrinologists, nutritionists & trainers)  
- 📊 **Custom lifestyle and clinical plans**  
- 🔄 **Ongoing monitoring and adaptation**  
- 💬 **All managed seamlessly within our app**
""")
    qr = Image.open("qr_code.png")
    st.image(qr, width=200)

    # Save quiz data once
    if sheet and not st.session_state.saved_quiz:
        try:
            row = [st.session_state.timestamp] + list(st.session_state.info.values()) + \
                  list(st.session_state.answers.values()) + [diagnosis]
            sheet.append_row(row)
            st.session_state.saved_quiz = True
        except:
            st.error("Failed to save quiz data.")

    st.markdown("---")
    st.subheader("📥 Join the InBalance Waitlist")
    join = st.radio("Would you like to join?", ["Yes", "No"], index=None)
    track = symptoms = goal = notes = ""

    if join == "Yes":
        track = st.radio("Do you track your cycle or symptoms?", ["App-based", "Manual", "Not yet", "Other"], index=None)
        symptoms = st.multiselect("Top symptoms you face:", [
            "Irregular cycles", "Cravings", "Low energy", "Mood swings",
            "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog"
        ])
        goal = st.radio("What’s your main health goal?", [
            "Understand my cycle", "Reduce symptoms", "Get diagnosis", 
            "Personalized plan", "Just curious"
        ], index=None)
        notes = st.text_area("Additional notes or questions:")

    if st.button("📧 Save & Finish"):
        if sheet and not st.session_state.saved_waitlist:
            try:
                row2 = [st.session_state.timestamp] + list(st.session_state.info.values()) + \
                       list(st.session_state.answers.values()) + [diagnosis, join, track or "", 
                       ", ".join(symptoms or []), goal or "", notes or ""]
                sheet.append_row(row2)
                st.success("✅ Saved! We'll contact you soon 💌")
            except:
                st.error("Failed to save waitlist info.")
            finally:
                # restart quiz
                st.session_state.clear()
                st.experimental_rerun()

    if st.button("🔁 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
