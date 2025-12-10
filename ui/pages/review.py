import streamlit as st
from ui.mcp_client import MCPClient

client = MCPClient()

st.title("Review Topic")

topic = st.session_state.get("selected_topic", None)
if not topic:
    st.warning("No topic selected for review.")
    st.stop()

st.subheader("Quick Summary")
st.write(f"This is a brief summary of **{topic}** based on syllabus extraction.")

def generate_mock_questions(topic: str):
    return [
        {
            "question": f"What best describes {topic}?",
            "options": ["Definition", "Example", "Algorithm", "Use-case"],
            "answer": 0,
        },
        {
            "question": f"Which part belongs to {topic}?",
            "options": ["Part A", "Part B", "Part C", "Not related"],
            "answer": 1,
        },
    ]

questions = generate_mock_questions(topic)
user_answers = []

for i, q in enumerate(questions):
    st.write(f"### {i+1}. {q['question']}")
    ans = st.radio("Choose:", q["options"], key=f"q{i}")
    user_answers.append(ans)

if st.button("Submit Answers"):
    score = 0
    for i, q in enumerate(questions):
        if q["options"].index(user_answers[i]) == q["answer"]:
            score += 1
            client.call_tool("knowledge.update", {"student_id": "user_1", "topic": topic, "delta": 5})
        else:
            client.call_tool("knowledge.update", {"student_id": "user_1", "topic": topic, "delta": -3})
    st.success(f"You scored {score}/{len(questions)}")

