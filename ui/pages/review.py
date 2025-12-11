import streamlit as st
import sys
import pathlib

# Ensure project root is available
# Logic: file is at ui/pages/review.py, parents[2] is root
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ui.mcp_client import MCPClient

client = MCPClient()

st.title("Review Topic")

topic = st.session_state.get("selected_topic", None)
if not topic:
    st.warning("No topic selected for review.")
    st.stop()

st.header(f"Topic: {topic}")

# --- Explanation ---
explain_key = f"explain_{topic}"
if explain_key not in st.session_state:
    with st.spinner("Generating explanation..."):
        # We assume context is not strictly needed or unavailable here, or could be fetched.
        # Prompt only asked to call 'llm.explain' for the selected topic.
        resp = client.call_tool("llm.explain", {"topic": topic})
        if isinstance(resp, dict):
            st.session_state[explain_key] = resp.get("explanation", str(resp))
        else:
            st.session_state[explain_key] = str(resp)

st.subheader("Explanation")
st.write(st.session_state[explain_key])

st.divider()

# --- Flashcards ---
fc_key = f"flashcards_{topic}"

if st.button("Generate Flashcards"):
    with st.spinner("Generating flashcards..."):
        resp = client.call_tool("llm.flashcards", {"topic": topic, "count": 5})
        # Check if fallback or real list
        if "flashcards" in resp:
            st.session_state[fc_key] = resp["flashcards"]
        else:
            st.error(f"Failed to generate flashcards: {resp.get('_raw', resp)}")

if fc_key in st.session_state:
    st.subheader("Flashcards")
    flashcards = st.session_state[fc_key]
    for i, fc in enumerate(flashcards):
        q_text = fc.get("q", "Question")
        a_text = fc.get("a", "Answer")
        with st.expander(f"Q{i+1}: {q_text}"):
            st.write(f"**Answer:** {a_text}")

st.divider()

# --- MCQs ---
mcq_key = f"mcqs_{topic}"

if st.button("Generate MCQs"):
    with st.spinner("Generating MCQs..."):
        resp = client.call_tool("llm.generate_mcq", {"topic": topic, "count": 3})
        if "mcqs" in resp:
            st.session_state[mcq_key] = resp["mcqs"]
        else:
            st.error(f"Failed to generate MCQs: {resp.get('_raw', resp)}")

if mcq_key in st.session_state:
    st.subheader("Quiz")
    mcqs = st.session_state[mcq_key]
    
    with st.form(key=f"quiz_form_{topic}"):
        answers = {}
        for i, q in enumerate(mcqs):
            st.markdown(f"**{i+1}. {q.get('question', 'Error loading question')}**")
            opts = q.get("options", [])
            # Index-based radio sometimes tricky if options are duplicates, but assuming unique
            answers[i] = st.radio(
                "Choose:", 
                options=opts, 
                key=f"radio_{topic}_{i}", 
                index=None
            )
            
        submitted = st.form_submit_button("Submit Answers")
        
        if submitted:
            score = 0
            total = len(mcqs)
            
            for i, q in enumerate(mcqs):
                user_choice = answers.get(i)
                correct_idx = q.get("answer_index", 0)
                
                # Safety check
                if 0 <= correct_idx < len(q.get("options", [])):
                    correct_text = q["options"][correct_idx]
                else:
                    correct_text = "Unknown"

                if user_choice == correct_text:
                    score += 1
                    client.call_tool("knowledge.update", {"student_id": "user_1", "topic": topic, "delta": 5})
                    st.success(f"Q{i+1}: Correct!")
                else:
                    client.call_tool("knowledge.update", {"student_id": "user_1", "topic": topic, "delta": -3})
                    st.error(f"Q{i+1}: Incorrect. The correct answer was: {correct_text}")
                    st.caption(f"Explanation: {q.get('explanation', '')}")
            
            st.metric("Final Score", f"{score}/{total}")
