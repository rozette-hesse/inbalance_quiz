import streamlit as st
import openai

# Load OpenAI API key from Streamlit Secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Teal primary theme override (optional)
st.markdown("""
    <style>
    .stButton>button {
        background-color: #2e9c91;
        color: white;
        border-radius: 5px;
    }
    .stRadio label {
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Set page config
st.set_page_config(page_title="InBalance Quiz", layout="centered")

# Center logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://raw.githubusercontent.com/rozette-hesse/inbalance_quiz/main/Logo-X-2024-01.png", width=150)

# Title and subtitle
st.markdown("<h1 style='text-align:center;'>🩺 Let’s Check In With Your Hormones</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Quick check for symptoms like hormonal imbalance, insulin resistance, or PCOS.</p>", unsafe_allow_html=True)

# Define questions and weights
questions = [
    {
        "key": "cycle",
        "question": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (on hormonal treatment or pregnant)",
            "Regular (25–35 days)",
            "Often irregular (<25 or >35 days)",
            "Rarely got my period (<6 times/year)"
        ],
        "weights": [0, 1, 6, 8],
        "cluster": "CA",  # Chronic Anovulation
        "multiplier": 4
    },
    {
        "key": "hair",
        "question": "Do you notice excessive thick black hair growth on your face, chest, or back?",
        "options": [
            "No, not at all.",
            "Yes, well-controlled with hair removal.",
            "Yes, major issue and resistant to removal.",
            "Yes, with scalp hair thinning or loss."
        ],
        "weights": [1, 5, 7, 8],
        "cluster": "HYPRA",  # HyperAndrogenism
        "multiplier": 4
    },
    {
        "key": "acne",
        "question": "Have you had issues with acne or oily skin in the past year?",
        "options": [
            "No skin issues.",
            "Yes, mild and controlled.",
            "Yes, often despite treatment.",
            "Yes, severe and persistent."
        ],
        "weights": [1, 4, 6, 8],
        "cluster": "HYPRA",
        "multiplier": 3
    },
    {
        "key": "weight",
        "question": "Have you experienced weight changes in the past year?",
        "options": [
            "Stable weight.",
            "Stable with effort.",
            "Gaining without major lifestyle change.",
            "Can’t lose despite diet/exercise."
        ],
        "weights": [1, 2, 5, 7],
        "cluster": "PCOMIR",  # Insulin Resistance / PCOS-like
        "multiplier": 2
    },
    {
        "key": "fatigue",
        "question": "Do you feel excessively tired or sleepy after meals?",
        "options": [
            "No, not really.",
            "Sometimes after heavy or sugary meals.",
            "Yes, often regardless of meal.",
            "Yes, almost daily and it affects alertness."
        ],
        "weights": [1, 2, 4, 6],
        "cluster": "PCOMIR",
        "multiplier": 1
    },
]

# Track state
if "q" not in st.session_state:
    st.session_state.q = 0
    st.session_state.answers = []

# Quiz logic
if st.session_state.q < len(questions):
    current = questions[st.session_state.q]
    
    # Centered question + radio
    st.markdown(f"<h4 style='text-align:center;'>{current['question']}</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        answer = st.radio("", current["options"], key=current["key"])

    if st.button("Next"):
        st.session_state.answers.append({
            "cluster": current["cluster"],
            "score": current["weights"][current["options"].index(answer)] * current["multiplier"]
        })
        st.session_state.q += 1
        st.rerun()
else:
    st.success("✅ All done! Analyzing your answers…")

    # Calculate cluster scores
    cluster_totals = {"CA": 0, "HYPRA": 0, "PCOMIR": 0}
    for ans in st.session_state.answers:
        cluster_totals[ans["cluster"]] += ans["score"]

    # Determine phenotype
    CA = cluster_totals["CA"]
    HYPRA = cluster_totals["HYPRA"]
    PCOMIR = cluster_totals["PCOMIR"]

    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        result = "HCA-PCO (Possible PCOS)"
    elif CA >= 20 and HYPRA >= 20:
        result = "H-CA (Possible PCOS)"
    elif HYPRA >= 20 and PCOMIR >= 10:
        result = "H-PCO (Possible PCOS)"
    elif CA >= 20 and PCOMIR >= 10:
        result = "PCO-CA (Possible PCOS)"
    else:
        result = "No significant PCOS pattern detected"

    st.markdown(f"<h2 style='text-align:center;'>🧬 Result: {result}</h2>", unsafe_allow_html=True)

    # AI feedback
    prompt = f"""The quiz detected: {result}.
    Please give a short, friendly explanation of what this might mean, and suggest one lifestyle tip or habit that can help improve hormonal balance."""

    try:
        ai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        advice = ai_response.choices[0].message.content.strip()
        st.info(advice)
    except:
        st.warning("Unable to fetch AI feedback. (OpenAI key missing or request failed)")

    st.markdown("---")
    st.markdown("📲 Want expert tracking & care?")
    st.markdown("[Join the waitlist here](https://linktr.ee/Inbalance.ai)")

    # Show QR
    st.image("https://raw.githubusercontent.com/rozette-hesse/inbalance_quiz/main/Grey%20White%20Simple%20Light%20Real%20Estate%20QR%20Code.png", width=120)

