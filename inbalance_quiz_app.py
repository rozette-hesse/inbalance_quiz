import streamlit as st
from PIL import Image

# Page setup (must be first!)
st.set_page_config(page_title="InBalance Quiz", layout="centered")

# Load images
logo = Image.open("logo.png")
qr = Image.open("qr_code.png")

# Style tweaks
st.markdown("""
    <style>
        .main {background-color: #ffffff;}
        h1 {color: #007C91;}
        .big-qr img {max-width: 150px !important;}
        .logo-center img {max-width: 150px !important;}
        .question {font-size: 18px; font-weight: bold;}
        .option {font-size: 16px;}
        .result-title {font-size: 24px; font-weight: 700; color: #007C91;}
        .footer {margin-top: 40px;}
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="logo-center">', unsafe_allow_html=True)
st.image(logo)
st.markdown('</div>', unsafe_allow_html=True)

st.title("InBalance Hormonal Health Quiz")
st.markdown("Take a 1-minute check for **hormonal imbalance, PCOS**, or **insulin resistance.**")

# Initialize session state
if "q" not in st.session_state:
    st.session_state.q = 0
    st.session_state.answers = []

# Questions and Weights
questions = [
    {
        "q": "How regular was your menstrual cycle in the past year?",
        "options": [
            "Does not apply (on hormonal treatment or pregnant)",
            "Regular (25–35 days)",
            "Often irregular (<25 or >35 days)",
            "Rarely got my period (<6 times/year)"
        ],
        "weights": [0, 1, 6, 8],
        "cluster": "CA",
        "multiplier": 4
    },
    {
        "q": "Do you notice excessive thick hair growth (face, chest, back)?",
        "options": [
            "No, not at all.",
            "Yes, it's noticeable and managed with hair removal.",
            "Yes, it's resistant to treatment.",
            "Yes, and I also have scalp hair thinning/loss."
        ],
        "weights": [1, 5, 7, 8],
        "cluster": "HYPRA",
        "multiplier": 4
    },
    {
        "q": "Have you had issues with acne or oily skin?",
        "options": [
            "No issues at all.",
            "Yes, but well-controlled.",
            "Yes, often despite treatment.",
            "Yes, severe and persistent."
        ],
        "weights": [1, 4, 6, 8],
        "cluster": "HYPRA",
        "multiplier": 3
    },
    {
        "q": "Have you experienced weight changes?",
        "options": [
            "No, stable weight.",
            "Stable with effort.",
            "Struggling despite no change in diet.",
            "Struggling despite diet and exercise."
        ],
        "weights": [1, 2, 5, 7],
        "cluster": "PCOMIR",
        "multiplier": 2
    },
    {
        "q": "Do you feel tired or sleepy after meals?",
        "options": [
            "No, not really.",
            "Sometimes, after sugary meals.",
            "Often, regardless of food.",
            "Almost daily fatigue after eating."
        ],
        "weights": [1, 2, 4, 6],
        "cluster": "PCOMIR",
        "multiplier": 1
    }
]

# Store clusters
cluster_scores = {"CA": 0, "HYPRA": 0, "PCOMIR": 0}

# Display current question
if st.session_state.q < len(questions):
    q = questions[st.session_state.q]
    st.markdown(f"<div class='question'>{q['q']}</div>", unsafe_allow_html=True)
    selected = st.radio(" ", q["options"], key=f"q{st.session_state.q}")
    
    if st.button("Next"):
        idx = q["options"].index(selected)
        score = q["weights"][idx] * q["multiplier"]
        cluster_scores[q["cluster"]] += score
        st.session_state.answers.append(idx)
        st.session_state.q += 1
        st.rerun()
else:
    # Diagnosis logic
    CA = cluster_scores["CA"]
    HYPRA = cluster_scores["HYPRA"]
    PCOMIR = cluster_scores["PCOMIR"]

    if CA >= 20 and HYPRA >= 20 and PCOMIR >= 10:
        result = "HCA-PCO (Likely PCOS)"
        msg = "You show signs of chronic anovulation, androgen excess, and insulin resistance. InBalance can help you monitor and treat all three."
    elif CA >= 20 and HYPRA >= 20:
        result = "H-CA (Hormonal + Irregular Cycles)"
        msg = "Signs of ovulatory dysfunction and hormonal imbalance. InBalance supports tracking symptoms and personalizing care."
    elif HYPRA >= 20 and PCOMIR >= 10:
        result = "H-PCO (Androgen + Metabolic)"
        msg = "You may be dealing with metabolic issues and androgen symptoms. InBalance can help you manage your symptoms and optimize hormones."
    elif CA >= 20 and PCOMIR >= 10:
        result = "PCO-CA (Irregular Cycles + Metabolic)"
        msg = "Cycle issues combined with metabolic strain. InBalance tracks both for better cycle control."
    elif CA >= 20:
        result = "Phenotype D (Irregular Cycles)"
        msg = "You show signs of cycle irregularity. Tracking with InBalance helps clarify patterns and guide care."
    elif HYPRA >= 20:
        result = "Phenotype C (Hormonal Imbalance)"
        msg = "Signs of elevated androgens like acne or excess hair. InBalance can help reduce and track flare-ups."
    elif PCOMIR >= 10:
        result = "Possible Insulin Resistance"
        msg = "You may be experiencing signs of insulin resistance. InBalance can help detect and manage these shifts."
    else:
        result = "No strong hormonal patterns detected."
        msg = "Your symptoms don't suggest a clear hormonal imbalance. Use InBalance to continue tracking and catch early signs."

    st.success("✅ All done! Analyzing your answers…")
    st.markdown(f"<div class='result-title'>🧬 Result: {result}</div>", unsafe_allow_html=True)
    st.write(msg)

    # Call to action
    st.markdown("---")
    st.markdown("💡 **Want expert tracking & care?**")
    st.image(qr, caption="Scan to start with InBalance", width=200)

    if st.button("🔄 Start Over"):
        st.session_state.q = 0
        st.session_state.answers = []
        st.rerun()
