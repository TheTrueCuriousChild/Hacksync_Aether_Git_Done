def judge_agent(prompt, round_no, memory):
    favor_points = memory["favor"]
    against_points = memory["against"]

    return (
        f"After reviewing Round {round_no}, both sides present valid arguments.\n\n"
        "• **Strongest Pro:** AI enables personalization and efficiency at scale.\n"
        "• **Strongest Con:** Human teachers provide irreplaceable emotional intelligence.\n\n"
        "⚖️ **Interim Verdict:** AI should act as a support system, not a replacement."
    )
