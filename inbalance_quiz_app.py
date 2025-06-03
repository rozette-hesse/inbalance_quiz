import streamlit as st
from PIL import Image

st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

if "q" not in st.session_state:
    st.session_state.q = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# Load Logo
st.image("logo.png", width=140)

st.markdown("""
<h2 style='text-align: center; color: teal;'>InBalance Hormonal Health Quiz</h2>
<p style='text-align: center;'>Take a quick check for <b>hormonal imbalance</b>, <b>PCOS</b>, or <b>insulin resistance</b>. Takes 1 minute.</p>
""", unsafe_allow_html=True)

questions = [
    {
        "text": "How regular was your menstrual cycle in the past year?",
        "options": [
            ("Does not apply (on hormonal treatment or pregnant)", 0),
            ("Regular (25–35 days)", 1),
            ("Often irregular (<25 or >35 days)", 6),
            ("Rarely got my period (<6 times/year)", 8)
        ],
        "cluster": "CA"
    },
    {
        "text": "Have you experienced excessive hair growth (face, chest, back)?",
        "options": [
            ("No, not at all", 1),
            ("Yes, but managed with removal techniques", 5),
            ("Yes, and it's hard to control", 7),
            ("Yes, plus scalp hair thinning", 8)
        ],
        "cluster": "HYPRA"
    },
    {
        "text": "Have you had acne or oily skin issues recently?",
        "options": [
            ("No, my skin is clear", 1),
            ("Yes, but it’s manageable", 4),
            ("Yes, it's often persistent", 6),
            ("Yes, severe and resistant to treatment", 8)
        ],
        "cluster": "HYPRA"
    },
    {
        "text": "Have you struggled with weight changes?",
        "options": [
            ("No, stable weight", 1),
            ("Some changes but manageable", 2),
            ("Struggling to control weight", 5),
            ("Hard to lose weight despite efforts", 7)
        ],
        "cluster": "PCOMIR"
    },
    {
        "text": "Do you feel unusually tired or sleepy after meals?",
        "options": [
            ("No, not really", 1),
            ("Sometimes after heavy/sugary meals", 2),
            ("Often, regardless of meals", 4),
            ("Almost daily, hard to stay alert", 6)
        ],
        "cluster": "PCOMIR"
    }
]

q_index = st.session_state.q
total_q = len(questions)

if q_index < total_q:
    q = questions[q_index]
    st.markdown(f"**Step {q_index + 1} of {total_q}**")
    option_texts = [opt[0] for opt in q["options"]]
    selection = st.radio(q["text"], option_texts, key=q_index)

    if st.button("Next"):
        selected_weight = dict(q["options"])[selection]
        st.session_state.answers.append({
            "cluster": q["cluster"],
            "weight": selected_weight,
            "text": q["text"],
            "choice": selection
        })
        st.session_state.q += 1
        st.rerun()

else:
    st.success("✅ All done! Analyzing your answers...")

    CA = sum(a["weight"] for a in st.session_state.answers if a["cluster"] == "CA") * 4
    HYPRA = sum(a["weight"] for a in st.session_state.answers if a["cluster"] == "HYPRA") * 1.5
    PCOMIR = sum(a["weight"] for a in st.session_state.answers if a["cluster"] == "PCOMIR")

    # Diagnosis logic
    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        result = "HCA-PCO (Classic PCOS)"
        summary = "You show signs of ovulation issues, high androgen levels, and metabolic symptoms — a classic PCOS pattern."
    elif CA >= 20 and HYPRA >= 20:
        result = "H-CA (Androgenic + Ovulatory)"
        summary = "You may have elevated androgens and irregular cycles. This might indicate PCOS or another hormonal disorder."
    elif HYPRA >= 20 and PCOMIR >= 10:
        result = "H-PCO (Androgen + Metabolic)"
        summary = "Your signs suggest hormonal and metabolic disruption, often linked to insulin resistance or a variant of PCOS."
    elif CA >= 20 and PCOMIR >= 10:
        result = "PCO-CA (Ovulatory + Metabolic)"
        summary = "You show cycle disturbances and energy/weight imbalance. This may signal early PCOS or metabolic irregularities."
    else:
        result = "No strong hormonal patterns detected"
        summary = "Your answers don’t show strong signs of PCOS or major hormonal dysfunction. That’s great — but keep monitoring your cycle."

    st.markdown(f"### 🧬 Result: **{result}**")
    st.markdown(f"**{summary}**")

    # -------------------- Personalized Answer Summary --------------------
    st.markdown("### 🧠 Your Responses & What They May Mean:")
    for answer in st.session_state.answers:
        if "irregular" in answer["choice"].lower():
            st.markdown("- 🩸 You reported **irregular cycles**, which may signal ovulatory dysfunction.")
        elif "hair" in answer["choice"].lower():
            st.markdown("- 💇 You mentioned **hair changes** — often linked to androgen levels.")
        elif "acne" in answer["choice"].lower() or "skin" in answer["choice"].lower():
            st.markdown("- 🌿 You noted **skin concerns**, which may be hormonal.")
        elif "weight" in answer["choice"].lower():
            st.markdown("- ⚖️ **Weight fluctuations** can be tied to insulin or hormonal resistance.")
        elif "tired" in answer["choice"].lower() or "sleepy" in answer["choice"].lower():
            st.markdown("- 😴 Feeling **fatigue after meals** may point to insulin sensitivity issues.")

    # -------------------- How InBalance Can Help --------------------
    st.markdown("""
    <div style='margin-top: 30px; padding: 20px; background-color: #e8f6f6; border-radius: 10px;'>
        <h4 style='color: teal;'>💡 How InBalance Can Help</h4>
        <p>InBalance helps you track your symptoms, cycle patterns, skin/hair changes, fatigue and weight — so our team of experts can guide you toward better hormonal balance.</p>
        <p>Whether you need to confirm a diagnosis, adjust your diet, or optimize workouts, we’ve got you covered with personalized support.</p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------- QR Code --------------------
    st.image("qr_code.png", width=180, caption="Scan to learn more")

    # -------------------- Restart --------------------
    st.button("🔁 Start Over", on_click=lambda: st.session_state.clear())
