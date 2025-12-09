import os
import sys
import pathlib
import streamlit as st
import pandas as pd
from ui.mcp_client import MCPClient

# Ensure project root is available so sibling packages import in Streamlit
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

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
    days = st.selectbox("Plan duration", [30, 60, 90])
    if st.button("Generate Study Plan"):
        plan_rows = []
        if topics:
            n = len(topics)
            for i, t in enumerate(topics):
                day_index = int(i * days / max(1, n))
                plan_rows.append({"Day": day_index + 1, "Topic": t})
            df = pd.DataFrame(plan_rows).sort_values("Day").reset_index(drop=True)
            st.subheader("Study Plan")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No topics available. Upload a syllabus first.")

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
                if st.button("Review This Topic", key=f"review_{name}"):
                    st.info(f"Starting review for: {name}")
        else:
            st.info("No weak topics found.")
    except Exception as e:
        st.warning(f"Unable to load weak topics: {e}")
