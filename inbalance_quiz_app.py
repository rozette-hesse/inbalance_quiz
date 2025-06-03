import streamlit as st
from PIL import Image
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# -------------------- CONFIG --------------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# -------------------- SETUP SESSION --------------------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "completed" not in st.session_state:
    st.session_state.completed = False

# -------------------- LOGO & HEADER --------------------
logo = Image.open("logo.png")
st.image(logo, width=100)

st.markdown(
    "<h1 style='text-align: center; color: teal;'>Check Your Hormonal Balance</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center;'>A 1-minute quiz to understand if your symptoms might suggest PCOS, insulin resistance, or hormonal imbalance.</p>",
    unsafe_allow_html=True,
)

# -------------------- NAME + EMAIL --------------------
if "name" not in st.session_state:
    st.session_state.name = ""
if "email" not in st.session_state:
    st.session_state.email = ""

if st.session_state.q_index == 0 and not st.session_state.completed:
    st.markdown("### 👋 Let's start by getting to know you")
    st.session_state.name = st.text_input("First name:")
    st.session_state.email = st.text_input("Email:")

    def is_valid_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)

    if st.button("Start Quiz"):
        if not st.session_state.name.strip():
            st.warning("Please enter your name.")
        elif not is_valid_email(st.session_state.email):
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.q_index += 1
            st.rerun()
    st.stop()

# -------------------- QUESTIONS --------------------
questions = [
    {
        "question": "How regular was your menstrual cycle in the past year?",
        "options": [
            ("Does not apply (use of hormonal treatments or pregnancies in the past year)", 0),
            ("Regular most of the time (25–35 days)", 1),
            ("Often irregular (< 25 days or > 35 days)", 6),
            ("I rarely got my period this year (< 6 periods)", 8),
        ],
    },
    {
        "question": "Do you notice excessive thick black hair growth on your face, chest, or back?",
        "options": [
            ("No, not at all.", 1),
            ("Yes, manageable with removal.", 5),
            ("Yes, major issue resistant to removal.", 7),
            ("Yes, and there's hair thinning on scalp.", 8),
        ],
    },
    {
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            ("No, no issues.", 1),
            ("Yes, but manageable.", 4),
            ("Yes, frequent issues.", 6),
            ("Yes, severe & resistant.", 8),
        ],
    },
    {
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            ("No, stable weight.", 1),
            ("Stable with healthy habits.", 2),
            ("Struggling to control weight.", 5),
            ("Struggling despite diet/workouts.", 7),
        ],
    },
    {
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            ("No, not really.", 1),
            ("Sometimes, after heavy/sugary meals.", 2),
            ("Yes, often regardless of food.", 4),
            ("Yes, daily difficulty staying alert.", 6),
        ],
    },
]

# -------------------- QUIZ FLOW --------------------
index = st.session_state.q_index

if 1 <= index <= len(questions):
    q = questions[index - 1]
    st.markdown(f"<h4><b>{q['question']}</b></h4>", unsafe_allow_html=True)
    answer = st.radio(" ", [opt[0] for opt in q["options"]], index=None, key=index)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back"):
            if st.session_state.q_index > 1:
                st.session_state.q_index -= 1
                st.session_state.answers.pop()
                st.rerun()
    with col2:
        if st.button("Next →"):
            if answer is None:
                st.warning("Please select an option before proceeding.")
            else:
                score = next(score for text, score in q["options"] if text == answer)
                st.session_state.answers.append(score)
                st.session_state.q_index += 1
                if st.session_state.q_index > len(questions):
                    st.session_state.completed = True
                st.rerun()

# ---------------------- RESULTS ----------------------
# DIAGNOSIS CLUSTER
if total < 8:
    diagnosis = "No strong hormonal patterns detected"
    explanation = f"""
    Your answers don’t currently show signs of major hormonal imbalance — that’s great!  
    Cycles seem balanced, and symptoms are within typical range.

    👉 Keep tracking your energy, skin, mood, and periods. Subtle shifts over time can reveal new patterns.  
    With InBalance, you can monitor changes early and take action when needed.
    """

elif total < 16:
    diagnosis = "Ovulatory Imbalance"
    explanation = f"""
    Your answers suggest that ovulation may not be happening regularly — or may be disrupted by stress, inflammation, or blood sugar swings.  
    These patterns often show up as irregular periods, fatigue, skin issues, or mood shifts.

    👉 Supporting ovulation through gentle lifestyle changes — like eating enough, sleeping better, and stabilizing blood sugar — can make a difference.  
    InBalance helps you see your personal patterns and guides you with expert-backed tips.
    """

elif total < 24:
    diagnosis = "HCA-PCO (Possible PCOS)"
    explanation = f"""
    Your symptoms align with common PCOS indicators — like irregular cycles, acne, hair changes, or difficulty managing weight.  
    While only a medical provider can confirm a diagnosis, these signs are worth understanding and addressing.

    👉 InBalance helps you get clarity, track what matters, and create a nutrition/symptom plan tailored to your type.  
    Our experts can help you feel more in control of your hormones and energy.
    """

else:
    diagnosis = "H-PCO (Androgenic + Metabolic Signs)"
    explanation = f"""
    Your answers suggest elevated androgens and possible insulin resistance — often seen in PCOS or metabolic imbalance.  
    This can impact your skin, hair, cycle, mood, and ability to manage weight.

    👉 InBalance gives you tools to balance blood sugar, reduce inflammation, and track improvements — while experts help guide your care.  
    A tailored plan (with food, movement, and stress tools) can support real hormonal change.
    """


    st.success("✅ Quiz complete.")
    st.markdown(f"### 🧬 Result: {diagnosis}")
    st.markdown(f"<p style='font-size: 16px;'>{explanation}</p>", unsafe_allow_html=True)

    st.info("💡 How InBalance Can Help")
    st.markdown("""
    InBalance helps you track symptoms, cycles, fatigue, skin changes, and more — and our experts use that data to guide your care.

    Whether you need a diagnosis, want to balance hormones, or just track better — we’ve got you.
    """)

    # ✅ QR Code for App Waitlist
    try:
        qr = Image.open("qr_code.png")
        st.image(qr, width=200)
    except:
        st.warning("⚠️ QR code image not found. Make sure `qr_code.png` is in your app folder.")

    # ✅ Waitlist CTA
    st.markdown("### 💬 Want to join the InBalance app waitlist?")
    join = st.radio("Join waitlist?", ["Yes", "No"], index=None, key="waitlist")

    extra_info = {}
    if join == "Yes":
        extra_info["Tracking"] = st.radio("Do you currently track your cycle or symptoms?", [
            "Yes, with an app",
            "Yes, manually",
            "No, but I want to",
            "No, and I don’t know where to start",
            "Other"
        ], index=None)

        extra_info["Symptoms"] = st.multiselect("What symptoms do you deal with most often?", [
            "Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating",
            "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"
        ])

        extra_info["Goal"] = st.radio("What is your main health goal right now?", [
            "Understand my cycle better",
            "Reduce symptoms like fatigue, acne, or cravings",
            "Looking for diagnosis",
            "Want a personalized lifestyle plan",
            "Just curious",
            "Other"
        ], index=None)

        extra_info["Notes"] = st.text_area("Anything you’d like us to know?")

    # ✅ Save to Google Sheets (Optional)
    if st.button("Finish & Save"):
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
            client = gspread.authorize(creds)
            sheet = client.open(st.secrets["google_sheets"]["sheet_name"])
            worksheet = sheet.worksheet(st.secrets["google_sheets"]["worksheet_name"])
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                st.session_state.name,
                st.session_state.email,
                total,
                diagnosis,
                explanation,
                extra_info.get("Tracking", ""),
                ", ".join(extra_info.get("Symptoms", [])),
                extra_info.get("Goal", ""),
                extra_info.get("Notes", ""),
            ]
            worksheet.append_row(row)
            st.success("✅ Your answers were saved.")
        except Exception as e:
            st.error("❌ Could not save your data.")
            st.text(str(e))

    st.button("Restart Quiz", on_click=lambda: st.session_state.clear())
