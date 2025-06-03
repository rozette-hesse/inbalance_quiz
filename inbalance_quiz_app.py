import streamlit as st
from PIL import Image

# Page setup
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# Load images
logo = Image.open("logo.png")
qr_code = Image.open("qr_code.png")

# Centered logo
st.image(logo, use_column_width=True)

# Title
st.markdown("<h1 style='text-align: center; color: teal;'>InBalance Hormonal Health Quiz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Take a 1-minute check for <strong>hormonal imbalance, PCOS</strong>, or <strong>insulin resistance</strong>.</p>", unsafe_allow_html=True)
st.markdown("---")

# Quiz questions
questions = [
    {
        "question": "How regular was your menstrual cycle in the past year?",
        "options": [
            ("Does not apply (use of hormonal treatments or pregnancies in the past year)", 0),
            ("Regular most of the time (25–35 days)", 1),
            ("Often irregular (< 25 days or > 35 days)", 6),
            ("I rarely got my period this year (< 6 periods)", 8)
        ]
    },
    {
        "question": "Do you notice excessive thick black hair growth on your face, chest, or back?",
        "options": [
            ("No, not at all.", 1),
            ("Yes, it’s a noticeable issue that is well-controlled with hair removal techniques.", 5),
            ("Yes, it’s a major issue that is resistant to hair removal techniques.", 7),
            ("Yes, excessive hair growth is an issue alongside hair thinning or hair-loss on the scalp", 8)
        ]
    },
    {
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            ("No, I'm not facing any skin troubles", 1),
            ("Yes, but well controlled with skin treatments", 4),
            ("Yes, often despite regular skin treatments", 6),
            ("Yes, severe and resistant to skin treatments", 8)
        ]
    },
    {
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            ("No, my weight is generally stable.", 1),
            ("No, my weight is more or less stable as long as I work out and eat mindfully.", 2),
            ("Yes, I’m struggling to control my weight without significant changes in diet and/or exercise.", 5),
            ("Yes, I’m struggling to lose weight despite diets and/or regular workouts.", 7)
        ]
    },
    {
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            ("No, not really.", 1),
            ("Sometimes after heavy or sugary meals.", 2),
            ("Yes, often regardless of what I eat.", 4),
            ("Yes, almost daily with trouble staying alert and awake after meals.", 6)
        ]
    }
]

# Score weight per question
weights = [4, 3, 2.5, 2, 1]

# Store answers
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
    st.session_state.total_score = 0
    st.session_state.selected_answers = []

# Display questions one by one
if st.session_state.q_index < len(questions):
    q = questions[st.session_state.q_index]
    st.markdown(f"<h3 style='color: black; font-size: 24px; font-weight: bold;'>{q['question']}</h3>", unsafe_allow_html=True)
    selected = st.radio(" ", [opt[0] for opt in q["options"]], index=None)

    if st.button("Next") and selected:
        points = dict(q["options"])[selected]
        st.session_state.total_score += points * weights[st.session_state.q_index]
        st.session_state.selected_answers.append(selected)
        st.rerun()

else:
    score = st.session_state.total_score

    # Determine diagnosis
    if score < 25:
        diagnosis = "No strong hormonal patterns detected"
        detail = "Your symptoms don’t show strong signs of PCOS or major hormonal dysfunction. That’s great — but keep monitoring your cycle."
    elif 25 <= score < 35:
        diagnosis = "Possible Ovulatory Imbalance"
        detail = "You may have signs of irregular ovulation, which can impact fertility or cycle regularity. Consider further hormonal testing."
    elif 35 <= score < 45:
        diagnosis = "Possible Metabolic-Hormonal Imbalance"
        detail = "You may have signs of both insulin resistance and hormonal dysregulation. A full checkup is recommended."
    elif 45 <= score < 55:
        diagnosis = "H-PCO (Androgenic PCOS)"
        detail = "Symptoms suggest elevated male hormones like testosterone — often linked to acne, hair growth, and cycle issues."
    else:
        diagnosis = "HCA-PCO (Classic PCOS)"
        detail = "Your symptoms are strongly suggestive of PCOS — including hormonal, cycle, and metabolic issues. A medical consult is highly recommended."

    # Header
    st.success("✅ All done! Analyzing your answers…")
    st.markdown(f"<h3 style='color: teal; margin-top: 20px;'>🧬 Result: {diagnosis}</h3>", unsafe_allow_html=True)
    st.write(f"**{detail}**")

    # Recommendations (based on selected options only — NOT showing answers)
    recs = []
    ans = st.session_state.selected_answers

    if "I rarely got my period" in ans[0] or "Often irregular" in ans[0]:
        recs.append("Cycle irregularity may signal ovulatory issues. Tracking ovulation patterns could be helpful.")

    if "hair thinning" in ans[1] or "major issue" in ans[1]:
        recs.append("Excessive hair growth + thinning may reflect high androgen levels (testosterone). Consider testing.")

    if "persistent" in ans[2] or "resistant" in ans[2]:
        recs.append("Persistent acne may signal inflammation or excess androgens.")

    if "struggling" in ans[3] or "lose weight despite" in ans[3]:
        recs.append("Weight struggles despite effort may suggest insulin resistance.")

    if "daily" in ans[4] or "often" in ans[4]:
        recs.append("Fatigue after meals may reflect unstable blood sugar or early insulin resistance.")

    if recs:
        st.markdown("### 🧠 How InBalance Can Help")
        with st.container():
            st.info(
                "InBalance helps you track symptoms, spot patterns, and make sense of skin, cycle, or energy changes — so you can take informed steps.\n\n" +
                "\n".join([f"- {r}" for r in recs])
            )

    # QR code & restart
    st.image(qr_code, caption="Scan to learn more", width=300)
    if st.button("🔁 Start Over"):
        st.session_state.q_index = 0
        st.session_state.total_score = 0
        st.session_state.selected_answers = []
        st.rerun()
