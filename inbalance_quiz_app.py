import streamlit as st
from PIL import Image

st.set_page_config(page_title="InBalance Hormonal Health Quiz", layout="centered")

# Initialize session state
if "q" not in st.session_state:
    st.session_state.q = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# Branding
st.image("logo.png", width=200)
st.markdown("""
<h2 style='text-align: center; color: teal;'>InBalance Hormonal Health Quiz</h2>
<p style='text-align: center;'>Quick check-in to see if your symptoms might signal a hormonal imbalance.</p>
""", unsafe_allow_html=True)

# Questions and mapped recommendations
questions = [
    {
        "text": "How regular was your menstrual cycle in the past year?",
        "options": {
            "Does not apply (e.g. pregnant or on hormonal birth control)": None,
            "Regular (25–35 days)": "✅ Your cycle seems balanced. Keep tracking it for changes.",
            "Often irregular (<25 or >35 days)": "🔁 Irregular cycles can suggest ovulatory issues or hormonal imbalance.",
            "Rarely got my period (<6 times/year)": "🚨 Very infrequent periods may signal ovulatory dysfunction or PCOS."
        }
    },
    {
        "text": "Have you experienced excessive hair growth (face, chest, back)?",
        "options": {
            "No, not at all": None,
            "Yes, but managed with removal techniques": "🧔‍♀️ Could be a sign of mild androgen excess.",
            "Yes, and it's hard to control": "⚠️ Persistent hair growth may point to high androgen levels.",
            "Yes, with scalp hair thinning": "🚩 Body + scalp hair changes may signal deeper hormonal imbalances."
        }
    },
    {
        "text": "Have you had acne or oily skin issues recently?",
        "options": {
            "No, my skin is clear": None,
            "Yes, but it’s manageable": "🧴 Mild hormonal acne is common — especially around ovulation.",
            "Yes, it's often persistent": "⚠️ Chronic acne may reflect elevated androgens or inflammation.",
            "Yes, severe and resistant to treatment": "🚨 Severe acne is often tied to hormonal or metabolic dysfunction."
        }
    },
    {
        "text": "Have you struggled with weight changes?",
        "options": {
            "No, stable weight": None,
            "Some changes but manageable": "📉 Slight weight shifts are normal — keep an eye on trends.",
            "Struggling to control weight": "⚠️ Could reflect metabolic slowdown or hormone shifts.",
            "Hard to lose weight despite efforts": "⚖️ Resistance to weight loss may be tied to insulin or cortisol levels."
        }
    },
    {
        "text": "Do you feel unusually tired or sleepy after meals?",
        "options": {
            "No, not really": None,
            "Sometimes after heavy/sugary meals": "🍬 You may be sensitive to sugar spikes — consider tracking your response.",
            "Often, regardless of meals": "⚠️ Frequent post-meal fatigue might reflect blood sugar or insulin issues.",
            "Almost daily, hard to stay alert": "🚨 Persistent energy crashes can indicate insulin resistance."
        }
    }
]

# Tag keywords for suggested pattern
diagnosis_keywords = {
    "Ovulatory Imbalance": ["period", "cycle", "ovulation"],
    "Androgen-Related": ["hair", "acne", "androgen"],
    "Metabolic/Insulin-Related": ["weight", "insulin", "fatigue", "sugar"]
}

# Ask questions
q_index = st.session_state.q
if q_index < len(questions):
    q = questions[q_index]
    st.markdown(f"<h4 style='font-size: 22px; font-weight: bold;'>{q['text']}</h4>", unsafe_allow_html=True)
    selected = st.radio("", list(q["options"].keys()), key=f"q{q_index}")
    if st.button("Next"):
        st.session_state.answers.append((q["options"][selected]))
        st.session_state.q += 1
        st.rerun()

# Final screen
else:
    st.success("✅ All done! Analyzing your answers…")

    # Show final diagnosis result
    st.markdown(f"""
    <h3 style='color: teal; margin-top: 20px;'>🧬 Result: {diagnosis}</h3>
    """, unsafe_allow_html=True)

    # Generate a personalized summary paragraph (based on feedback messages from answers)
    feedback_lines = [f for f in st.session_state.answers if f]
    
    if not feedback_lines:
        personalized_summary = (
            "Your answers don’t show strong signs of hormonal imbalance. "
            "That’s great — but it’s still important to stay in tune with your cycle."
        )
    else:
        personalized_summary = " ".join(feedback_lines)

    st.markdown(f"""
    <div style='padding: 20px; background-color: #f1fcf9; border-radius: 10px; font-size: 16px; line-height: 1.6'>
        💡 <strong>Your personalized insight:</strong><br><br>
        {personalized_summary}
    </div>
    """, unsafe_allow_html=True)

    # How InBalance Can Help (static content)
    st.markdown(f"""
    <div style='padding: 20px; background-color: #e8f6f6; border-radius: 10px; margin-top: 20px;'>
        <h4 style='color: teal;'>How InBalance Can Help</h4>
        <p>InBalance helps you monitor symptoms like acne, fatigue, irregular cycles or sugar crashes — and understand how they connect to your hormones.</p>
        <p>Our team of experts helps you move from confusion to clarity with cycle-synced nutrition, lifestyle and fitness tracking.</p>
        <p>You deserve personalized care — and we’re here for it.</p>
    </div>
    """, unsafe_allow_html=True)

    # QR code and restart
    st.image("qr_code.png", width=300)
    st.markdown("<p style='text-align: center;'>Scan to follow us or get early access 💙</p>", unsafe_allow_html=True)
    st.button("🔁 Start Over", on_click=lambda: st.session_state.clear())
