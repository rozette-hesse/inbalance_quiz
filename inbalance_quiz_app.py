import streamlit as st
from PIL import Image
import re
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# ---------------- LOGO ------------------
logo = Image.open("logo.png")
st.image(logo, width=120)

st.markdown("""
<h1 style='text-align: center; color: teal;'>Check Your Hormonal Balance</h1>
<p style='text-align: center;'>A 1-minute quiz to understand if your symptoms might suggest PCOS, insulin resistance, or hormonal imbalance.</p>
""", unsafe_allow_html=True)

# ----------- INIT SESSION STATE -------------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "completed" not in st.session_state:
    st.session_state.completed = False

# ----------- EMAIL VALIDATION -------------
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# ----------- GET USER NAME/EMAIL -------------
if "name" not in st.session_state:
    st.session_state.name = ""
if "email" not in st.session_state:
    st.session_state.email = ""

if st.session_state.q_index == 0 and not st.session_state.completed:
    st.markdown("### 👋 Let's start with your name and email")
    st.session_state.name = st.text_input("First name")
    st.session_state.email = st.text_input("Email address")

    if st.button("Start Quiz"):
        if not st.session_state.name.strip():
            st.warning("Please enter your name to continue.")
        elif not is_valid_email(st.session_state.email):
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.q_index += 1
            st.rerun()
    st.stop()

# ----------- QUESTIONS ---------------------
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
            ("Yes, well controlled with hair removal.", 5),
            ("Yes, major issue and resistant to removal.", 7),
            ("Yes, plus hair loss on scalp.", 8),
        ],
    },
    {
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            ("No skin issues", 1),
            ("Yes, but well controlled", 4),
            ("Yes, persistent", 6),
            ("Yes, resistant to treatment", 8),
        ],
    },
    {
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            ("Stable", 1),
            ("Stable with mindful habits", 2),
            ("Gaining weight without major lifestyle changes", 5),
            ("Can't lose weight despite efforts", 7),
        ],
    },
    {
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            ("No", 1),
            ("Sometimes after sugar-heavy meals", 2),
            ("Yes, often regardless of food", 4),
            ("Yes, nearly daily fatigue after meals", 6),
        ],
    },
]

# ----------- DISPLAY QUESTION ---------------------
if st.session_state.q_index <= len(questions):
    q_id = st.session_state.q_index - 1
    q = questions[q_id]
    st.markdown(f"### {q['question']}")
    selected = st.radio(" ", [opt[0] for opt in q["options"]], key=f"q_{q_id}")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back") and st.session_state.q_index > 1:
            st.session_state.q_index -= 1
            st.session_state.answers.pop()
            st.rerun()
    with col2:
        if st.button("Next ➡️"):
            score = next(val for txt, val in q["options"] if txt == selected)
            st.session_state.answers.append(score)
            st.session_state.q_index += 1
            st.rerun()

# ----------- DIAGNOSIS ---------------------
if st.session_state.q_index > len(questions) and not st.session_state.completed:
    score = sum(st.session_state.answers)
    if score < 8:
        diagnosis = "No strong hormonal patterns detected"
        explain = "Your symptoms don’t currently show signs of hormonal dysfunction. Great — but keep monitoring regularly."
    elif score < 16:
        diagnosis = "Ovulatory Imbalance"
        explain = "You may have hormonal fluctuations affecting ovulation. These can show as irregular cycles, fatigue, or mood changes."
    elif score < 24:
        diagnosis = "HCA-PCO (Possible PCOS)"
        explain = "You show symptoms that may align with PCOS, such as acne, weight gain, or irregular periods."
    else:
        diagnosis = "H-PCO (Androgen + Metabolic Signs)"
        explain = "Your symptoms suggest signs of hormonal + metabolic imbalance — possibly PCOS or insulin resistance."

    st.session_state.diagnosis = diagnosis
    st.session_state.explain = explain
    st.session_state.q_index += 1
    st.rerun()

# ----------- FOLLOW-UP + SAVE DATA ---------------------
if st.session_state.completed == False and st.session_state.q_index == len(questions) + 1:
    st.success("✅ Done! Here's your personalized result.")
    st.markdown(f"### 🧬 Result: {st.session_state.diagnosis}")
    st.markdown(f"**{st.session_state.explain}**")

    st.info("💡 How InBalance Can Help")
    st.markdown("""
InBalance helps you track symptoms, cycles, skin/hair changes, energy, and more.
We guide you with expert-based recommendations to manage hormonal balance through lifestyle, nutrition, and care.
""")

    join = st.radio("Would you like to join our waitlist?", ["Yes", "No"])
    if join == "Yes":
        method = st.radio("Do you currently track your cycle or symptoms?", [
            "Yes, with an app", "Yes, manually", "No, but I want to", "No, and I don’t know where to start", "Other"])
        symptoms = st.multiselect("What symptoms do you deal with most often?", [
            "Irregular cycles", "Cravings", "Low energy", "Mood swings", "Bloating",
            "Acne", "Anxiety", "Sleep issues", "Brain fog", "Other"])
        goal = st.radio("What is your main health goal?", [
            "Understand my cycle", "Reduce symptoms", "Get a diagnosis",
            "Create a lifestyle plan", "Just curious", "Other"])
        notes = st.text_area("Anything else you'd like to share?")

        # ✅ Save all this to Google Sheets if needed using gspread here
        # This would be the spot for saving the collected data.

    st.session_state.completed = True
    st.button("Restart", on_click=lambda: st.session_state.clear())
