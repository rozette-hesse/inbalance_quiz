import streamlit as st
import time
from PIL import Image

# -------------------- CONFIG --------------------
st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# -------------------- SESSION STATE --------------------
if "q" not in st.session_state:
    st.session_state.q = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "transition" not in st.session_state:
    st.session_state.transition = False

# -------------------- IMAGES --------------------
st.image("logo.png", width=180)

st.markdown("""
    <h2 style='text-align: center; color: teal;'>InBalance Hormonal Health Quiz</h2>
    <p style='text-align: center;'>Take a quick check for <b>hormonal imbalance</b>, <b>PCOS</b>, or <b>insulin resistance</b>. Takes 1 minute.</p>
""", unsafe_allow_html=True)

# -------------------- QUESTIONS --------------------
questions = [
    {
        "text": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (on hormonal treatment or pregnant)",  # 0
            "Regular (25–35 days)",                                # 1
            "Often irregular (<25 or >35 days)",                   # 6
            "Rarely got my period (<6 times/year)"                # 8
        ],
        "weights": [0, 1, 6, 8],
        "cluster": "CA"
    },
    {
        "text": "Have you experienced excessive hair growth (face, chest, back)?",
        "options": [
            "No, not at all",                                     # 1
            "Yes, but managed with removal techniques",           # 5
            "Yes, and it's hard to control",                      # 7
            "Yes, plus scalp hair thinning"                       # 8
        ],
        "weights": [1, 5, 7, 8],
        "cluster": "HYPRA"
    },
    {
        "text": "Have you had acne or oily skin issues recently?",
        "options": [
            "No, my skin is clear",                               # 1
            "Yes, but it’s manageable",                           # 4
            "Yes, it's often persistent",                         # 6
            "Yes, severe and resistant to treatment"              # 8
        ],
        "weights": [1, 4, 6, 8],
        "cluster": "HYPRA"
    },
    {
        "text": "Have you struggled with weight changes?",
        "options": [
            "No, stable weight",                                  # 1
            "Some changes but manageable",                        # 2
            "Struggling to control weight",                       # 5
            "Hard to lose weight despite efforts"                 # 7
        ],
        "weights": [1, 2, 5, 7],
        "cluster": "PCOMIR"
    },
    {
        "text": "Do you feel unusually tired or sleepy after meals?",
        "options": [
            "No, not really",                                     # 1
            "Sometimes after heavy/sugary meals",                 # 2
            "Often, regardless of meals",                         # 4
            "Almost daily, hard to stay alert"                    # 6
        ],
        "weights": [1, 2, 4, 6],
        "cluster": "PCOMIR"
    }
]

# -------------------- TRANSITION --------------------
if st.session_state.transition:
    st.info("Loading next question...")
    time.sleep(1)
    st.session_state.transition = False
    st.session_state.q += 1

# -------------------- QUIZ FLOW --------------------
q_index = st.session_state.q
total_q = len(questions)

if q_index < total_q:
    q = questions[q_index]
    st.markdown(f"**Step {q_index + 1} of {total_q}**")
    user_ans = st.radio(q["text"], q["options"], key=q_index)

    if st.button("Next"):
        st.session_state.answers.append({
            "cluster": q["cluster"],
            "weight": q["weights"][q["options"].index(user_ans)]
        })
        st.session_state.transition = True
        st.rerun()

# -------------------- SCORING --------------------
else:
    st.success("✅ All done! Analyzing your answers...\n")

    CA = sum(a["weight"] for a in st.session_state.answers if a["cluster"] == "CA") * 4
    HYPRA = sum(a["weight"] for a in st.session_state.answers if a["cluster"] == "HYPRA")
    HYPRA = HYPRA * 1.5  # Adjusting overall weight to reflect importance
    PCOMIR = sum(a["weight"] for a in st.session_state.answers if a["cluster"] == "PCOMIR")

    # Diagnosis logic
    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        result = "HCA-PCO (Classic PCOS)"
        explanation = "You show signs of ovulation issues, elevated androgens, and possible insulin resistance — a classic PCOS profile. We recommend getting expert evaluation."
    elif CA >= 20 and HYPRA >= 20:
        result = "H-CA (Androgenic + Ovulatory)"
        explanation = "You may be experiencing both androgenic symptoms and menstrual irregularities. This may indicate PCOS or similar hormonal imbalance."
    elif HYPRA >= 20 and PCOMIR >= 10:
        result = "H-PCO (Androgen + Metabolic)"
        explanation = "Your signs suggest androgen elevation and insulin resistance. This could reflect a metabolic form of PCOS or other endocrine disorder."
    elif CA >= 20 and PCOMIR >= 10:
        result = "PCO-CA (Ovulatory + Metabolic)"
        explanation = "Your symptoms show ovulation issues and metabolic imbalance. You may benefit from cycle and lifestyle tracking."
    else:
        result = "No strong hormonal patterns detected"
        explanation = "Your answers don’t show strong signs of PCOS or major hormonal dysfunction. That’s great — but keep monitoring your cycle."

    st.markdown(f"### 🧬 Result: **{result}**")
    st.markdown(f"**{explanation}**")

    # -------------------- INBALANCE RECOMMENDATION --------------------
    st.markdown("""
    <div style='margin-top: 30px; padding: 20px; background-color: #e6f2f2; border-radius: 10px;'>
        <h4 style='color: teal;'>💡 How InBalance Can Help</h4>
        <p>InBalance helps you track your symptoms, cycle patterns, skin/hair changes, fatigue and weight — so our team of experts can guide you toward better hormonal balance.</p>
        <p>Whether you need to confirm a diagnosis, adjust your diet, or optimize workouts, we’ve got you covered.</p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------- QR CODE --------------------
    st.image("qr_code.png", width=200, caption="Scan to learn more", use_column_width=False)

    # -------------------- RESTART --------------------
    st.button("🔁 Start Over", on_click=lambda: st.session_state.clear())
