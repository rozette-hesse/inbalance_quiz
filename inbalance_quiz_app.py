import streamlit as st
from PIL import Image
import re

# ----------------------- CONFIG -----------------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# ----------------------- STATE INIT -----------------------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "completed" not in st.session_state:
    st.session_state.completed = False

# ----------------------- LOGO & HEADER -----------------------
logo = Image.open("logo.png")
st.image(logo, width=120)

st.markdown("""
<h1 style='text-align: center; color: teal;'>Check Your Hormonal Balance</h1>
<p style='text-align: center;'>A 1-minute quiz to understand if your symptoms might suggest PCOS, insulin resistance, or hormonal imbalance.</p>
""", unsafe_allow_html=True)

# ----------------------- EMAIL VALIDATION -----------------------
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# ----------------------- USER INFO -----------------------
if "name" not in st.session_state:
    st.session_state.name = ""
if "email" not in st.session_state:
    st.session_state.email = ""

if st.session_state.q_index == 0 and not st.session_state.completed:
    st.markdown("### 👋 Let's start by getting to know you")
    st.session_state.name = st.text_input("Your first name")
    st.session_state.email = st.text_input("Your email address")

    if st.button("Start Quiz"):
        if not st.session_state.name.strip():
            st.warning("Please enter your name.")
        elif not is_valid_email(st.session_state.email):
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.q_index = 1
            st.rerun()
    st.stop()

# ----------------------- QUESTIONS -----------------------
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
            ("Yes, well-controlled with hair removal.", 5),
            ("Yes, and resistant to hair removal.", 7),
            ("Yes, with scalp hair thinning too.", 8),
        ],
    },
    {
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            ("No skin issues", 1),
            ("Yes, but controlled", 4),
            ("Yes, often and hard to manage", 6),
            ("Yes, severe and persistent", 8),
        ],
    },
    {
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            ("Weight stable", 1),
            ("Stable with effort", 2),
            ("Struggling to control weight", 5),
            ("Gaining despite workouts", 7),
        ],
    },
    {
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            ("No", 1),
            ("Sometimes after sugar", 2),
            ("Yes, often", 4),
            ("Yes, daily fatigue after meals", 6),
        ],
    },
]

# ----------------------- QUIZ FLOW -----------------------
index = st.session_state.q_index

if index <= len(questions) - 1:
    q = questions[index]
    st.markdown(f"<h4 style='font-weight: bold;'>{q['question']}</h4>", unsafe_allow_html=True)
    selected = st.radio(" ", [opt[0] for opt in q["options"]], key=index)

    if st.button("Next"):
        score = next(val for txt, val in q["options"] if txt == selected)
        st.session_state.answers.append(score)
        st.session_state.q_index += 1
        st.rerun()

elif index == len(questions):
    st.markdown("**Would you like to join our app waitlist for expert hormonal tracking?**")
    join = st.radio(" ", ["Yes", "No"], key="waitlist")

    if join == "Yes":
        st.markdown("### 💬 Just a few more quick questions!")

        st.session_state.track_cycle = st.radio(
            "Do you currently track your cycle or symptoms?",
            [
                "Yes, with an app",
                "Yes, manually",
                "No, but I want to",
                "No, and I don’t know where to start",
                "Other"
            ],
            key="track"
        )

        st.session_state.symptoms = st.multiselect(
            "What symptoms do you deal with most often?",
            [
                "Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating",
                "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"
            ],
            key="symptoms"
        )

        st.session_state.goal = st.radio(
            "What is your main health goal right now?",
            [
                "I want to understand my cycle better",
                "I want to reduce symptoms like fatigue, acne, or cravings",
                "I’m looking for a diagnosis or medical answers",
                "I want a personalized lifestyle plan (nutrition, supplements, etc.)",
                "I'm just curious for now",
                "Other"
            ],
            key="goal"
        )

        st.session_state.notes = st.text_area("Anything you’d like us to know?", key="notes")

    if st.button("Finish"):
        st.session_state.completed = True
        st.session_state.join_waitlist = join
        st.rerun()


# ----------------------- RESULTS -----------------------
if st.session_state.completed:
    score = sum(st.session_state.answers)

    if score < 8:
        diag = "No strong hormonal patterns detected"
        detail = "You don’t currently show strong signs of hormonal dysfunction — but it’s smart to keep monitoring changes."
    elif score < 16:
        diag = "Ovulatory Imbalance"
        detail = "You may have mild cycle or ovulation issues like fatigue, acne, or irregular cycles."
    elif score < 24:
        diag = "HCA-PCO (Possible PCOS)"
        detail = "You show signs of PCOS — such as irregular cycles, excess androgens, or insulin-related symptoms."
    else:
        diag = "H-PCO (Androgenic + Metabolic)"
        detail = "You may have both hormonal and metabolic symptoms seen in PCOS and insulin resistance."

    st.success("✅ All done! Analyzing your results...")
    st.markdown(f"<h3 style='color: teal;'>🧬 Result: {diag}</h3>", unsafe_allow_html=True)
    st.markdown(f"**{detail}**")

    st.info("💡 How InBalance Can Help")
    st.markdown("""
    InBalance helps you track symptoms, cycles, skin/hair changes, energy and weight — so our expert team can guide you.
    
    Whether you’re confirming a diagnosis, adjusting nutrition, or optimizing workouts — we’ve got your back.
    """)

    qr = Image.open("qr_code.png")
    st.image(qr, width=200)

    if st.session_state.join_waitlist == "Yes":
        st.success("🎉 You’re on the waitlist! We’ll be in touch soon.")

    st.markdown("---")
    st.button("Start Over", on_click=lambda: st.session_state.clear())
