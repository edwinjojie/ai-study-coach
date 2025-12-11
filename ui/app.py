import os
import sys
import pathlib
import streamlit as st
import pandas as pd

# Ensure project root is available so sibling packages import in Streamlit
# Logic: file is at ui/app.py, parents[1] is root
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Now imports from 'ui' and 'services' will work
from ui.mcp_client import MCPClient
from services.syllabus_service import SyllabusService

client = MCPClient()

st.set_page_config(page_title="AI Study Coach", layout="wide")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Upload Syllabus",
    "Extracted Topics",
    "Study Plan",
    "Mastery Progress",
    "Weak Topics",
])

with tab1:
    pdf = st.file_uploader("Upload Syllabus PDF")
    if pdf is not None:
        base_dir = os.path.join("students", "user_1")
        os.makedirs(base_dir, exist_ok=True)
        pdf_path = os.path.join(base_dir, "syllabus.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf.getbuffer())
        service = SyllabusService()
        extracted_text = service.extract_text_from_pdf(pdf_path)
        result = client.call_tool("syllabus.parse", {"text": extracted_text})
        st.session_state["topics"] = result.get("topics", [])
        st.success("Syllabus processed")
        st.text_area("Preview", value=extracted_text, height=300)

with tab2:
    topics = st.session_state.get("topics")
    if topics:
        with st.expander("Extracted Topics", expanded=True):
            for t in topics:
                st.write(f"- {t}")
    else:
        st.info("No syllabus uploaded")

with tab3:
    topics = st.session_state.get("topics", [])
    # If no topics in session, try getting from knowledge graph if available
    if not topics:
         try:
            res = client.call_tool("knowledge.get_graph", {"student_id": "user_1"})
            g = res.get("graph", {}).get("topics", {})
            topics = list(g.keys())
         except:
            pass

    days = st.selectbox("Plan duration (days)", [3, 7, 14, 30], index=1)
    
    if st.button("Generate Study Plan"):
        if not topics:
            st.warning("No topics found. Please upload a syllabus or ensure knowledge graph is populated.")
        else:
            with st.spinner("Consulting LLM for personalized plan..."):
                # Get current mastery
                try:
                    res = client.call_tool("knowledge.get_graph", {"student_id": "user_1"})
                    graph_topics = res.get("graph", {}).get("topics", {})
                    # Simplify state to topic->mastery map
                    student_state = {t: data.get("mastery", 0) for t, data in graph_topics.items()}
                except:
                    student_state = {}

                plan_response = client.call_tool("llm.studyplan", {
                    "topics": topics, 
                    "days": days, 
                    "student_state": student_state
                })
                
                # Store
                if "plan" in plan_response:
                    st.session_state["generated_plan"] = plan_response
                else:
                    st.error(f"Error generating plan: {plan_response.get('_raw', 'Unknown error')}")

    if "generated_plan" in st.session_state:
        plan_data = st.session_state["generated_plan"]
        st.subheader("Personalized Plan Summary")
        st.write(plan_data.get("plan_text", ""))
        
        # Build DataFrame
        plan_list = plan_data.get("plan", [])
        if plan_list:
            display_rows = []
            for day_obj in plan_list:
                d = day_obj.get("day", 0)
                tasks = day_obj.get("tasks", [])
                # If tasks is list of strings
                if isinstance(tasks, list):
                    for t in tasks:
                        display_rows.append({"Day": d, "Task": t})
            
            if display_rows:
                df = pd.DataFrame(display_rows)
                st.dataframe(df, use_container_width=True)

with tab4:
    try:
        result = client.call_tool("knowledge.get_graph", {"student_id": "user_1"})
        graph = result.get("graph", {})
        topics = graph.get("topics", {})
        rows = [
            {
                "Topic": name,
                "Mastery": float(data.get("mastery", 0)),
                "Attempts": int(data.get("attempts", 0)),
            }
            for name, data in topics.items()
        ]
        if rows:
            st.subheader("Mastery Progress")
            st.dataframe(pd.DataFrame(rows), use_container_width=True)
            for name, data in topics.items():
                st.write(name)
                st.progress(int(float(data.get("mastery", 0))))
        else:
            st.info("No topics in knowledge graph yet.")
    except Exception as e:
        st.warning(f"Unable to load knowledge graph: {e}")

with tab5:
    try:
        weak = client.call_tool("knowledge.get_weak_topics", {"student_id": "user_1", "limit": 5})
        result = client.call_tool("knowledge.get_graph", {"student_id": "user_1"})
        graph = result.get("graph", {})
        topics = graph.get("topics", {})
        names = weak.get("topics", [])
        if names:
            st.subheader("Weakest Topics")
            for name in names:
                mastery = float(topics.get(name, {}).get("mastery", 0))
                st.write(f"{name} — {int(mastery)}% mastery")
                if st.button(f"Review {name}", key=f"review_{name}"):
                    st.session_state["selected_topic"] = name
                    st.switch_page("Review")
        else:
            st.info("No weak topics found.")
    except Exception as e:
        st.warning(f"Unable to load weak topics: {e}")
