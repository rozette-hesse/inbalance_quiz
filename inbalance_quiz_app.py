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
    st.session_state.saved = False
    st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ─── GOOGLE SHEETS ────────────────────────────────────────────
try:
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    st.error("⚠️ Google Sheet not connected.")
    sheet = None

# ─── QUESTIONS ────────────────────────────────────────────────
questions = {
    "Q1": ("How regular was your menstrual cycle in the past year?", [
        "Does not apply (e.g., hormonal treatment or pregnancy)",
        "Regular (25–35 days)",
        "Often irregular (<25 or >35 days)",
        "Rarely got period (<6 times/year)"
    ]),
    "Q2": ("Do you notice excessive thick black hair on face, chest, or back?", [
        "No, not at all",
        "Yes, manageable with removal",
        "Yes, resistant to removal",
        "Yes + scalp thinning or hair loss"
    ]),
    "Q3": ("Have you had acne or oily skin this year?", [
        "No",
        "Yes, mild and manageable",
        "Yes, frequent despite treatment",
        "Yes, severe and persistent"
    ]),
    "Q4": ("Have you experienced weight changes?", [
        "Stable weight",
        "Stable only with effort",
        "Struggling to maintain weight",
        "Can’t lose weight despite diet/exercise"
    ]),
    "Q5": ("Do you feel tired or sleepy after meals?", [
        "No",
        "Sometimes after heavy meals",
        "Yes, regardless of food",
        "Yes, almost daily with alertness issues"
    ]),
}

# ─── UTILITIES ────────────────────────────────────────────────
def get_country_choices():
    lst = []
    for c in pycountry.countries:
        try:
            code = phonenumbers.country_code_for_region(c.alpha_2)
            emoji = chr(127397 + ord(c.alpha_2[0])) + chr(127397 + ord(c.alpha_2[1]))
            lst.append(f"{emoji} {c.name} (+{code})")
        except:
            pass
    return sorted(set(lst))

def validate_phone(country, num):
    try:
        if not country or not num: return True
        cc = country.split("(+")[1].split(")")[0]
        return phonenumbers.is_valid_number(phonenumbers.parse(f"+{cc}{num}"))
    except:
        return False

# ─── INTRO PAGE ──────────────────────────────────────────────
if st.session_state.page == "intro":
    st.title("How Balanced Are Your Hormones?")
    st.subheader("A quick quiz to assess hormonal health & how InBalance can support you.")

    fn = st.text_input("First Name")
    ln = st.text_input("Last Name")
    email = st.text_input("Email")
    countries = get_country_choices()
    country = st.selectbox("Country (optional)", [""] + countries)
    phone = st.text_input("Phone (no spaces, optional)")

    if st.button("Start Quiz"):
        if not fn.strip() or not ln.strip() or not email.strip():
            st.warning("Please enter name and email.")
        elif not validate_phone(country, phone):
            st.warning("Phone number doesn't match selected country code.")
        else:
            st.session_state.info = {"First Name": fn, "Last Name": ln, "Email": email,
                                     "Country": country, "Phone": phone}
            st.session_state.page = "quiz"
            st.rerun()

# ─── QUIZ PAGE ───────────────────────────────────────────────
elif st.session_state.page == "quiz":
    st.header("📝 Answer All Questions")
    for key, (text, opts) in questions.items():
        st.session_state.answers[key] = st.radio(text, opts, key=key)

    if st.button("Submit Answers"):
        if any(ans is None for ans in st.session_state.answers.values()):
            st.warning("Please answer all questions.")
        else:
            st.session_state.page = "results"
            st.rerun()

# ─── RESULTS + WAITLIST PAGE ─────────────────────────────────
elif st.session_state.page == "results":
    q = st.session_state.answers
    diag = "Mild Hormonal Imbalance"
    r = []

    if "irregular" in q["Q1"].lower() or "rarely" in q["Q1"].lower():
        diag = "Cycle Irregularity"
        r.append("🗓️ Your cycles are inconsistent—try tracking ovulation symptoms or basal temperature.")
    if "resistant" in q["Q2"].lower() or "scalp" in q["Q2"].lower():
        diag = "Potential PCOS"
        r.append("🧬 Excess facial/body hair may point to androgen imbalance—consider endocrine evaluation.")
    if "oily" in q["Q3"].lower() or "persistent" in q["Q3"].lower():
        r.append("💊 Persistent acne can be hormone-related—our clinicians can tailor a combined approach.")
    if "struggling" in q["Q4"].lower() or "can’t" in q["Q4"].lower():
        diag = "H-PCO (Hormonal & Metabolic)"
        r.append("🥗 Difficulty losing weight despite effort? A metabolic-focused nutrition + training plan can help.")
    if "yes" in q["Q5"].lower():
        r.append("🍽️ Feeling sleepy after meals? Balancing blood sugar with structured meals may improve energy.")

    st.subheader(f"🧬 Diagnosis: {diag}")
    st.markdown("#### Recommendations for your answers:")
    for rec in r:
        st.info(rec)
    st.warning("⚠️ INFORMATION ONLY. Always consult a physician before making medical decisions.")

    st.markdown("### 💡 Why InBalance Helps")
    st.success("""
- 🧠 Phase-accurate tracking of symptoms & cycles  
- 🩺 Access to gynecologists, endocrinologists, nutritionists & trainers  
- 📊 Personalized lifestyle, nutrition & metabolic plans  
- 🔁 Ongoing adjustments & expert follow-up  
- 💬 Everything managed via a seamless app experience
""")
    st.image("qr_code.png", width=140)

    # Save quiz results once
    if sheet and not st.session_state.saved:
        try:
            row = [st.session_state.timestamp] + list(st.session_state.info.values()) \
                  + list(st.session_state.answers.values()) + [diag]
            sheet.append_row(row)
            st.session_state.saved = True
        except:
            st.error("Failed saving quiz data.")

    # WAITLIST
    st.markdown("---")
    st.subheader("📥 Join the InBalance Waitlist")
    join = st.radio("Would you like to join?", ["Yes", "No"], index=None)
    track = multi = goal = notes = None

    if join == "Yes":
        track = st.radio("Do you track your cycle/symptoms?", 
                         ["Yes, with app", "Yes, manually", "Not yet", "Other"], index=None)
        multi = st.multiselect("Top symptoms you face:", ["Irregular cycles", "Cravings", "Low energy",
                                                         "Mood swings", "Bloating", "Acne", 
                                                         "Anxiety", "Sleep issues", "Brain fog"])
        goal = st.radio("Main health goal:", 
                        ["Understand my cycle", "Reduce symptoms", "Get diagnosis", "Personalized plan", "Just curious"],
                        index=None)
        notes = st.text_area("Other notes you'd like to share:")

    if st.button("📧 Save & Finish"):
        if sheet:
            try:
                row2 = [st.session_state.timestamp] + list(st.session_state.info.values()) \
                       + list(st.session_state.answers.values()) + [diag, join, track or "", 
                                                                    ", ".join(multi or []), 
                                                                    goal or "", notes or ""]
                sheet.append_row(row2)
                st.success("✅ Saved! We'll be in touch 💌")
            except:
                st.error("Could not save waitlist info.")

    if st.button("🔄 Restart Quiz"):
        st.session_state.clear()
        st.rerun()
