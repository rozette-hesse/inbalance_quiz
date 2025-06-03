import streamlit as st
import openai

# --- CONFIG ---
st.set_page_config(page_title="InBalance Quiz", layout="centered")

# --- STYLING ---
st.markdown("""
    <style>
        h1, h2, h3, .stTextInput label, .stRadio label {
            color: #008080;
            font-family: 'Helvetica', sans-serif;
        }
        .stButton>button {
            background-color: #008080;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 0.5em 1em;
        }
        .stButton>button:hover {
            background-color: #006666;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.image("https://raw.githubusercontent.com/rozette-hesse/inbalance_quiz/main/Logo-X-2024-01.png", width=100)
st.markdown("<h1 style='text-align: center;'>InBalance Hormonal Health Quiz</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Quick check for symptoms like hormonal imbalance, insulin resistance, or PCOS.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- INITIALIZE SESSION ---
if 'q' not in st.session_state:
    st.session_state.q = 0
    st.session_state.answers = []

questions = [
    {
        "question": "1. How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (on hormonal treatment or pregnant)",
            "Regular (25–35 days)",
            "Often irregular (<25 or >35 days)",
            "Rarely got my period (<6 times/year)"
        ]
    },
    {
        "question": "2. Do you notice thick black hair on your face, chest, or back?",
        "options": [
            "No",
            "Yes, but well-controlled",
            "Yes, hard to manage",
            "Yes + scalp hair loss"
        ]
    },
    {
        "question": "3. Have you had acne or oily skin in the past year?",
        "options": [
            "No",
            "Yes, mild",
            "Yes, moderate",
            "Yes, severe and resistant to treatment"
        ]
    },
    {
        "question": "4. Have you experienced weight changes recently?",
        "options": [
            "No, stable",
            "Stable with effort",
            "Struggling to maintain",
            "Struggling to lose despite effort"
        ]
    },
    {
        "question": "5. Do you feel tired or sleepy after meals?",
        "options": [
            "No",
            "Sometimes after heavy meals",
            "Often regardless of food",
            "Almost daily"
        ]
    }
]

# --- QUESTION FLOW ---
if st.session_state.q < len(questions):
    current = questions[st.session_state.q]
    answer = st.radio(current["question"], current["options"])
    if st.button("Next"):
        st.session_state.answers.append(answer)
        st.session_state.q += 1
        st.rerun()
else:
    st.success("✅ All done! Analyzing your answers...")

    # --- MAPPING SCORING ---
    score_map = {
        0: {"Does not apply (on hormonal treatment or pregnant)": 0, "Regular (25–35 days)": 1, "Often irregular (<25 or >35 days)": 6, "Rarely got my period (<6 times/year)": 8},
        1: {"No": 1, "Yes, but well-controlled": 5, "Yes, hard to manage": 7, "Yes + scalp hair loss": 8},
        2: {"No": 1, "Yes, mild": 4, "Yes, moderate": 6, "Yes, severe and resistant to treatment": 8},
        3: {"No, stable": 1, "Stable with effort": 2, "Struggling to maintain": 5, "Struggling to lose despite effort": 7},
        4: {"No": 1, "Sometimes after heavy meals": 2, "Often regardless of food": 4, "Almost daily": 6}
    }

    # --- SCORE CALC ---
    cycle = score_map[0][st.session_state.answers[0]]
    hair = score_map[1][st.session_state.answers[1]]
    acne = score_map[2][st.session_state.answers[2]]
    weight = score_map[3][st.session_state.answers[3]]
    fatigue = score_map[4][st.session_state.answers[4]]

    CA = cycle * 4
    HYPRA = hair * 4 + acne * 3
    PCOMIR = weight * 2 + fatigue

    # --- DIAGNOSIS LOGIC ---
    phenotype = ""
    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        phenotype = "HCA-PCO (Possible PCOS)"
    elif CA >= 20 and HYPRA >= 20:
        phenotype = "H-CA (Hyperandrogenism + Cycle Irregularity)"
    elif HYPRA >= 20 and PCOMIR >= 10:
        phenotype = "H-PCO (Metabolic + Androgen Imbalance)"
    elif CA >= 20:
        phenotype = "Anovulatory Pattern"
    elif PCOMIR >= 10:
        phenotype = "Possible Insulin Resistance"
    else:
        phenotype = "No major indicators"

    st.markdown(f"<h2 style='color:#008080;'>🧬 Result: {phenotype}</h2>", unsafe_allow_html=True)

    # --- OPENAI DIAGNOSIS (Optional) ---
    openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else "your-api-key-here"

    prompt = f"""
    A user completed a 5-question hormonal health screening with the following responses:
    1. Cycle: {st.session_state.answers[0]}
    2. Hair: {st.session_state.answers[1]}
    3. Acne: {st.session_state.answers[2]}
    4. Weight: {st.session_state.answers[3]}
    5. Fatigue: {st.session_state.answers[4]}

    Based on this, provide:
    - A possible hormonal or metabolic interpretation
    - A simple health recommendation
    Keep it to 3 short sentences.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        feedback = response['choices'][0]['message']['content']
        st.info(feedback)
    except Exception as e:
        st.warning("Unable to fetch AI feedback. (OpenAI key missing or request failed)")

    # --- QR & CTA ---
    st.markdown("---")
    st.markdown("📲 Want expert tracking & care?")
    st.markdown("[Join the waitlist here](https://linktr.ee/Inbalance.ai)")
    st.image("https://raw.githubusercontent.com/rozette-hesse/inbalance_quiz/main/Grey%20White%20Simple%20Light%20Real%20Estate%20QR%20Code.png", width=160)
