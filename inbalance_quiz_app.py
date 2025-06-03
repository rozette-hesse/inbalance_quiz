import streamlit as st
from PIL import Image

# ----------------------- CONFIG -----------------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# ---------------------- LOGO & HEADER ----------------------
logo = Image.open("logo.png")
st.image(logo, width=150)

st.markdown(
    "<h1 style='text-align: center; color: teal;'>Check Your Hormonal Balance</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center;'>A 1-minute quiz to understand if your symptoms might suggest PCOS, insulin resistance, or hormonal imbalance.</p>",
    unsafe_allow_html=True,
)

# ---------------------- USER INFO ----------------------
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    name = st.text_input("Your Name")
    email = st.text_input("Email")
    if name and email:
        if st.button("Start Quiz"):
            st.session_state.started = True
            st.session_state.answers = []
            st.session_state.q_index = 0
    st.stop()

# ---------------------- QUIZ QUESTIONS ----------------------
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
            ("Yes, it’s a noticeable issue that is well-controlled with hair removal techniques.", 5),
            ("Yes, it’s a major issue that is resistant to hair removal techniques.", 7),
            ("Yes, excessive hair growth is an issue alongside hair thinning or hair-loss on the scalp", 8),
        ],
    },
    {
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            ("No, I'm not facing any skin troubles", 1),
            ("Yes, but well controlled with skin treatments", 4),
            ("Yes, often despite regular skin treatments", 6),
            ("Yes, severe and resistant to skin treatments", 8),
        ],
    },
    {
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            ("No, my weight is generally stable.", 1),
            ("No, my weight is more or less stable as long as I work out and eat mindfully.", 2),
            ("Yes, I’m struggling to control my weight without significant changes in diet and/or exercise.", 5),
            ("Yes, I’m struggling to lose weight despite diets and/or regular workouts.", 7),
        ],
    },
    {
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            ("No, not really.", 1),
            ("Sometimes after heavy or sugary meals.", 2),
            ("Yes, often regardless of what I eat.", 4),
            ("Yes, almost daily with trouble staying alert and awake after meals.", 6),
        ],
    },
]

# ---------------------- QUIZ FLOW ----------------------
index = st.session_state.q_index
question = questions[index]
st.markdown(f"<h4><b>{question['question']}</b></h4>", unsafe_allow_html=True)

option = st.radio(" ", [opt[0] for opt in question["options"]], key=index)

if st.button("Next"):
    selected_score = [opt[1] for opt in question["options"] if opt[0] == option][0]
    st.session_state.answers.append(selected_score)
    st.session_state.q_index += 1

    if st.session_state.q_index >= len(questions):
        st.session_state.completed = True
    st.rerun()

# ---------------------- RESULTS ----------------------
if st.session_state.get("completed"):
    total_score = sum(st.session_state.answers)

    # DIAGNOSIS CLUSTERING
    if total_score < 8:
        diagnosis = "No strong hormonal patterns detected"
        explanation = "Your symptoms don’t currently show strong signs of PCOS or major hormonal dysfunction. That’s great — but it’s still important to keep tracking your cycle regularly."
    elif total_score < 16:
        diagnosis = "Ovulatory Imbalance"
        explanation = "You may have signs of hormonal fluctuations that could affect ovulation. These can show up as acne, irregular cycles, or fatigue."
    elif total_score < 24:
        diagnosis = "HCA-PCO (Possible PCOS)"
        explanation = "Some of your symptoms align with common PCOS features — such as cycle irregularity, skin or hair changes, or weight gain."
    else:
        diagnosis = "H-PCO (Androgenic & Metabolic Signs)"
        explanation = "Your answers suggest possible hormonal and metabolic imbalances often seen in PCOS or insulin resistance."

    # FINAL MESSAGE
    st.success("✅ Quiz complete. Analyzing your answers...")
    st.markdown(f"<h3 style='color: teal; margin-top: 20px;'>🧬 Result: {diagnosis}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p><b>{explanation}</b></p>", unsafe_allow_html=True)

    st.info("💡 How InBalance Can Help")
    st.markdown("""
    InBalance helps you track your symptoms, cycle patterns, skin/hair changes, fatigue and weight — so our team of experts can guide you toward better hormonal balance.

    Whether you need to confirm a diagnosis, adjust your diet, or optimize workouts, we’ve got you covered.
    """)

    # QR Code
    qr = Image.open("qr_code.png")
    st.image(qr, width=200)

    # Waitlist CTA
    st.markdown("**Would you like to join our app waitlist for expert hormonal tracking?**")
    join = st.radio(" ", ["Yes", "No"])
    if join == "Yes":
        st.success("🎉 You're on the list! We'll be in touch soon.")

    st.button("Restart", on_click=lambda: st.session_state.clear())
