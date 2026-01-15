import streamlit as st

st.set_page_config(
    page_title="AI Debate Arena",
    layout="wide",
)
st.title("AI Debate Arena")

with st.container():
    prompt = st.text_area(
        "Debate Question",
        placeholder="Enter the debate question here...",
        height=80
    )
    col1, col2, col3, col4 = st.columns([2,1,1,2])
    with col1:
        start= st.button("Start Debate", use_container_width=True)
    with col2:
        rounds = st.selectbox("Rounds", [1, 3, 5, 7, 9], index=2)
    with col3:
        tone = st.selectbox("Tone", ["Balanced", "Aggressive", "Humorous", "Formal"], index=0)   
    with col4:
        allow_interaction = st.toggle("Allow agents to respond to each other")
st.divider()
favor_col, against_col, neutral_col, judge_col = st.columns(4)

def agent_card(title, icon, color):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            padding:12px;
            border-radius:12px;
            font-weight:bold;
            text-align:center;
            color:white;
        ">
            {icon} {title}
        </div>
        """,
        unsafe_allow_html=True
    )
if start and prompt.strip():
    for round_no in range(1, rounds + 1):

        with favor_col:
            agent_card("In Favor", "✅", "#2EAD8E")
            st.markdown(f"**Round {round_no}**")
            st.write("AI improves scalability, personalization, and access to education.")
            st.caption("Responding to prompt")

        with against_col:
            agent_card("Against", "❌", "#E5533D")
            st.markdown(f"**Round {round_no}**")
            st.write("Human teachers provide emotional intelligence and mentorship.")
            st.caption("Responding to In Favor agent")

        with neutral_col:
            agent_card("Neutral", "⚖️", "#F2B84B")
            st.markdown(f"**Round {round_no}**")
            st.write("AI can assist teachers but should not replace them entirely.")
            st.caption("Balanced perspective")

        with judge_col:
            agent_card("The Judge", "👩‍⚖️", "#4A6FA5")
            st.markdown(f"**Round {round_no} Verdict**")
            st.write("""
            - Strongest Pro: Personalization & scalability  
            - Strongest Con: Emotional intelligence  
            - Interim Verdict: AI as a support tool
            """)
            st.caption("Synthesizing arguments")

        st.divider()
