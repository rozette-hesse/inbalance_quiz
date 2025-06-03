import streamlit as st
from PIL import Image
import openai
import os

# ✅ Set Streamlit page config FIRST
st.set_page_config(page_title="InBalance Quiz", layout="centered")

# Load OpenAI key securely
api_key = st.secrets.get("OPENAI_API_KEY", "")
if api_key:
    openai.api_key = api_key

# Load logo and QR code
logo = Image.open("logo.png")
qr_code = Image.open("qr_code.png")

# --- UI Styling ---
st.image(logo, width=100)
st.markdown("## 💠 InBalance Hormonal Health Quiz")
st.markdown(
    "Check your symptoms for hormonal imbalance, PCOS or insulin resistance. Takes 1 minute!"
)
st.markdown("---")

# --- Questions ---
questions = [
    {
        "question": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (on hormonal treatment or pregnant)",
            "Regular (25–35 days)",
            "Often irregular (<25 or >35 days)",
            "Rarely got my period (<6 times/year)"
        ],
        "weights": [0, 1, 6, 8],
        "multiplier": 4
    },
    {
        "question": "Do you notice excessive thick black hair on your face, chest, or back?",
        "options": [
            "No, not at all",
            "Yes, but manageable with hair removal",
            "Yes, major issue, hard to manage",
            "Yes, and also losing hair on my scalp"
        ],
        "weights": [1, 5, 7, 8],
        "multiplier": 3
    },
    {
        "question": "Have you had issues with acne or oily skin?",
        "options": [
            "No skin problems",
            "Yes, controlled with treatment",
            "Yes, frequent despite treatment",
            "Yes, severe and resistant"
        ],
        "weights": [1, 4, 6, 8],
        "multiplier": 2.5
    },
    {
        "question": "Have you struggled with weight changes?",
        "options": [
            "No, my weight is stable",
            "Stable with effort",
            "Hard to control without major changes",
            "Hard to lose despite efforts"
        ],
        "weights": [1, 2, 5, 7],
        "multiplier": 2
    },
    {
        "question": "Do you feel tired or sleepy after meals?",
        "options": [
            "No",
            "Sometimes after sugar",
            "Yes, often",
            "Yes, almost daily"
        ],
        "weights": [1, 2, 4, 6],
        "multiplier": 1
    }
]

# Initialize session
if "q" not in st.session_state:
    st.session_state.q = 0
    st.session_state.answers = []

# --- Display question ---
q_index = st.session_state.q
if q_index < len(questions):
    q = questions[q_index]
    st.write(f"**{q['question']}**")
    selected = st.radio("", q["options"], key=f"q{q_index}")

    if st.button("Next"):
        option_index = q["options"].index(selected)
        score = q["weights"][option_index] * q["multiplier"]
        st.session_state.answers.append(score)
        st.session_state.q += 1
        st.rerun()

# --- Results ---
else:
    st.success("✅ All done! Analyzing your answers…")
    total_score = sum(st.session_state.answers)

    # Cluster logic
    CA = st.session_state.answers[0]  # Menstrual
    HIRSUTISM = st.session_state.answers[1] * 4
    ACNE = st.session_state.answers[2] * 3
    HYPRA = HIRSUTISM + ACNE
    PCOMIR = st.session_state.answers[3] + st.session_state.answers[4]

    # Diagnose based on cluster thresholds
    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        diagnosis = "HCA-PCO (Possible PCOS)"
    elif CA >= 20 and HYPRA >= 20:
        diagnosis = "H-CA (Hormonal Imbalance)"
    elif HYPRA >= 20 and PCOMIR >= 10:
        diagnosis = "H-PCO (Androgen + Metabolic)"
    elif CA >= 20 and PCOMIR >= 10:
        diagnosis = "PCO-CA (Cycle + Metabolic)"
    else:
        diagnosis = "No strong hormonal patterns detected."

    st.markdown(f"### 🧬 Result: **{diagnosis}**")

    # --- AI recommendation ---
    if api_key:
        try:
            prompt = (
                f"The user was diagnosed with: {diagnosis}. "
                "Give one short, evidence-based tip in less than 50 words to help support her hormonal balance."
            )
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
            )
            feedback = response.choices[0].message.content
            st.info(f"💡 AI Tip: {feedback}")
        except Exception as e:
            st.warning("⚠️ Unable to fetch AI tip. Please try again later.")
    else:
        st.warning("🔒 No OpenAI key set. Tip not available.")

    st.markdown("---")
    st.markdown("Want expert tracking & care?")

    st.markdown("[👉 Join the waitlist here](https://linktr.ee/Inbalance.ai)")

    st.image(qr_code, width=100)

    if st.button("Start Over"):
        st.session_state.q = 0
        st.session_state.answers = []
        st.rerun()
