import streamlit as st
from PIL import Image
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import phonenumbers
import pycountry

st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")
st.image(Image.open("logo.png"), width=120)

# --- Session State init ---
if "started" not in st.session_state:
    st.session_state.started = False
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- Country list with flags ---
countries = []
for country in pycountry.countries:
    code = f"+{phonenumbers.country_code_for_region(country.alpha_2)}"
    emoji = "".join(chr(0x1F1E6 + ord(c) - ord('A')) for c in country.alpha_2)
    countries.append(f"{emoji} {country.name} ({code})")
countries = sorted(set(countries))

# --- Connect to Google Sheets ---
try:
    creds_info = st.secrets["gcp_service_account"]
    scope = ["...spreadsheets","...drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    sheet = gspread.authorize(creds).open("InBalance_Quiz_Responses").sheet1
except:
    sheet = None

# --- Intro Form ---
if not st.session_state.started:
    st.title("How Balanced Are Your Hormones?")
    st.text_input("👩 First Name", key="first")
    st.text_input("👩 Last Name", key="last")
    st.text_input("📧 Email", key="email")
    country_sel = st.selectbox("🌍 Country", countries, index=0, key="country_full")
    st.text_input("📱 Phone (no spaces)", key="phone")
    if st.button("Start Quiz"):
        # validations
        if not st.session_state.first.strip() or not st.session_state.last.strip():
            st.warning("Enter both first and last name.")
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", st.session_state.email):
            st.warning("Invalid email.")
        else:
            region = country_sel[-3:-1]
            try:
                pn = phonenumbers.parse(st.session_state.phone, region)
                if not phonenumbers.is_valid_number(pn):
                    st.warning("Invalid phone for selected country.")
                    st.stop()
            except:
                st.warning("Invalid phone for country.")
                st.stop()
            st.session_state.started = True
            st.rerun()
    st.stop()

# --- Questions Page ---
questions = [
    ("How regular was your menstrual cycle in the past year?", [
        "Does not apply (e.g., hormonal treatment or pregnancy)",
        "Regular (25–35 days)",
        "Often irregular (<25 or >35 days)",
        "Rarely got period (<6 times a year)"
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

if st.session_state.started and not st.session_state.submitted:
    st.header("📝 Answer All Questions")
    for i, (q, opts) in enumerate(questions, start=1):
        st.markdown(f"**{i}. {q}**")
        st.session_state.answers[i] = st.radio("", opts, key=f"q{i}", index=None)
    if st.button("See Results"):
        missing = [i for i, _ in enumerate(questions, start=1)
                   if not st.session_state.answers.get(i)]
        if missing:
            st.warning("Please answer all questions.")
        else:
            st.session_state.submitted = True
            st.rerun()
    st.stop()

# --- Results and Recommendations ---
if st.session_state.submitted:
    st.success("✅ Quiz complete!")
    sel = st.session_state.answers
    st.header("🧬 Diagnosis & Personalized Insights")

    recs = []
    if sel[1].startswith("Often irregular") or sel[1].startswith("Rarely"):
        recs.append("Your cycle suggests potential ovulatory dysfunction. Track ovulation and consult for PCOS or thyroid.")
    if "resistant" in sel[2] or "scalp" in sel[2]:
        recs.append("Facial/body hair signals elevated androgens. InBalance experts can guide nutrition and stress protocols.")
    if "despite" in sel[3] or "severe" in sel[3]:
        recs.append("Persistent acne often ties to inflammation. Track it to a cycle phase and explore anti-inflammatory nutrition.")
    if "Can't lose" in sel[4] or "Struggling" in sel[4]:
        recs.append("Difficulty losing weight may point to insulin or cortisol issues. A metabolic plan with timing and movement helps.")
    if "daily" in sel[5] or "often" in sel[5]:
        recs.append("Post‑meal fatigue suggests blood sugar swings. Explore food timing and smart carb/protein combo.")

    # show diag and recs
    diag = "Hormonal Imbalance Pattern"
    st.subheader(f"🔬 Diagnosis: {diag}")
    for r in recs:
        st.info(r)

    st.warning("⚠️ This is for informational purposes only. Always consult your physician.")

    st.markdown("💡 **Why InBalance Helps You**")
    st.markdown(
        """
🗓️ **Precision cycle & symptom phase tracking** — understand each day’s hormonal context<br>
🔁 **Phase-based recommendations** tailored to your current symptoms<br>
👩‍⚕️ **Direct access to gynecologists, endocrinologists, nutritionists, and trainers**<br>
📊 **Data-driven insights** for personalized lifestyle and clinical care<br>
💛 **Ongoing support** to guide and adjust your journey
""", unsafe_allow_html=True)

    st.image("qr_code.png", width=180)

    st.markdown("### 💬 Want to join the InBalance waitlist?")
    join = st.radio("", ["Yes", "No"], index=None, key="join")
    extra = {}
    if join == "Yes":
        extra["tracking"] = st.radio(
            "Do you currently track your cycle/symptoms?",
            ["Yes, with an app", "Yes, manually", "No, but I want to", "No, don’t know where to start", "Other"]
        )
        extra["symptoms"] = st.multiselect(
            "What symptoms do you deal with most often?",
            ["Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating", "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"]
        )
        extra["goal"] = st.radio(
            "Your main health goal:",
            ["Understand my cycle", "Reduce symptoms", "Looking for diagnosis", "Clinical/lifestyle plan", "Just curious", "Other"]
        )
        extra["notes"] = st.text_area("Anything else you'd like us to know?")

    if st.button("Finish & Save"):
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            st.session_state.first,
            st.session_state.last,
            st.session_state.email,
            st.session_state.country_full.split("(")[-1].strip(")"),
            st.session_state.phone,
        ]
        row += [st.session_state.answers[i] for i in range(1, len(questions)+1)]
        row += [join]
        if join == "Yes":
            row += [extra.get(k, "") for k in ["tracking", "symptoms", "goal", "notes"]]
        if sheet:
            try:
                sheet.append_row(row)
                st.success("✅ Your responses were saved!")
            except Exception as e:
                st.error(f"❌ Saving error: {e}")
        else:
            st.error("❌ Google sheet unavailable.")
        st.stop()
