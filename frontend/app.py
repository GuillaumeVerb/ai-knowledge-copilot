from __future__ import annotations

import json
import os
from typing import Any

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Knowledge Copilot", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(244, 180, 0, 0.10), transparent 28%),
                radial-gradient(circle at top right, rgba(9, 132, 227, 0.10), transparent 32%),
                linear-gradient(180deg, #f8fafc 0%, #eef3f9 100%);
        }
        .hero {
            padding: 1.4rem 1.5rem;
            border-radius: 22px;
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #38bdf8 100%);
            color: white;
            box-shadow: 0 20px 50px rgba(15, 23, 42, 0.20);
            margin-bottom: 1rem;
        }
        .metric-card {
            padding: 0.9rem 1rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(15, 23, 42, 0.08);
            backdrop-filter: blur(10px);
        }
        .source-card {
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: #f8fafc;
            border-left: 4px solid #0ea5e9;
            margin-bottom: 0.8rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def call_api(method: str, path: str, **kwargs) -> Any:
    response = requests.request(method, f"{API_BASE_URL}{path}", timeout=120, **kwargs)
    response.raise_for_status()
    return response.json()


def api_get(path: str, **params):
    return call_api("GET", path, params=params)


def api_post(path: str, **kwargs):
    return call_api("POST", path, **kwargs)


def api_delete(path: str):
    return call_api("DELETE", path)


def render_source(source: dict[str, Any]) -> None:
    location = f"page {source['page_number']}" if source.get("page_number") else "document context"
    st.markdown(
        f"""
        <div class="source-card">
            <strong>{source['document_name']}</strong><br/>
            <small>{location}</small>
            <div style="margin-top:0.45rem;">{source['excerpt']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_history_item(item: dict[str, Any]) -> None:
    with st.container(border=True):
        st.markdown(f"**Q:** {item['question']}")
        st.write(item["answer"])
        st.caption(f"Latency: {item['latency_ms']} ms")


try:
    health = api_get("/health")
    api_online = health.get("status") == "ok"
except Exception:
    api_online = False

documents = api_get("/documents") if api_online else []
history = api_get("/history") if api_online else []
document_options = {doc["original_filename"]: doc["id"] for doc in documents}
indexed_count = len([doc for doc in documents if doc["status"] == "indexed"])

st.markdown(
    """
    <div class="hero">
        <h1 style="margin:0 0 0.35rem 0;">AI Knowledge Copilot</h1>
        <p style="margin:0; font-size:1.02rem; max-width:800px;">
            Upload internal knowledge, ask grounded questions, compare documents, and demo sourced AI answers
            in a polished interface ready for portfolio use.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Workspace")
    if api_online:
        st.success("Backend connected")
    else:
        st.error("Backend unavailable")
        st.caption("Expected API base URL: " + API_BASE_URL)
    st.markdown("### Quick stats")
    st.metric("Documents", len(documents))
    st.metric("Indexed", indexed_count)
    st.metric("History entries", len(history))
    st.markdown("### Demo flow")
    st.caption("1. Seed or upload documents")
    st.caption("2. Ask a grounded question")
    st.caption("3. Inspect sources and excerpts")
    st.caption("4. Compare two procedures")

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.markdown(
    f'<div class="metric-card"><strong>{len(documents)}</strong><br/>documents</div>',
    unsafe_allow_html=True,
)
metric_col2.markdown(
    f'<div class="metric-card"><strong>{indexed_count}</strong><br/>indexed</div>',
    unsafe_allow_html=True,
)
metric_col3.markdown(
    f'<div class="metric-card"><strong>{len(history)}</strong><br/>recent queries</div>',
    unsafe_allow_html=True,
)

tab_documents, tab_chat = st.tabs(["Documents", "Chat"])

with tab_documents:
    st.subheader("Upload")
    uploaded_file = st.file_uploader("Supported: PDF, DOCX, TXT, MD")
    tags_input = st.text_input("Tags (comma separated)", placeholder="hr, onboarding")
    if st.button("Upload document", use_container_width=True, disabled=uploaded_file is None or not api_online):
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        with st.spinner("Uploading and indexing document..."):
            result = api_post(
                "/documents/upload",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                data={"tags": json.dumps(tags)},
            )
        st.success(result["message"])
        st.rerun()

    st.subheader("Library")
    filter_tag = st.text_input("Filter by tag", key="filter_tag")
    filter_status = st.selectbox("Status", options=["", "indexed", "processing", "failed"])
    search_query = st.text_input("Search document name")
    filtered_documents = (
        api_get("/documents", tag=filter_tag or None, status=filter_status or None, search=search_query or None)
        if api_online
        else []
    )
    if not filtered_documents:
        st.info("No documents imported yet.")
    for document in filtered_documents:
        with st.container(border=True):
            col1, col2, col3 = st.columns([5, 2, 2])
            col1.markdown(f"**{document['original_filename']}**")
            col1.caption(f"Status: {document['status']} | Tags: {', '.join(document['tags']) or 'none'}")
            if col2.button("Summarize", key=f"summary_{document['id']}", use_container_width=True):
                summary = api_post(f"/documents/{document['id']}/summary")
                st.info(summary["summary"])
            if col3.button("Delete", key=f"delete_{document['id']}", use_container_width=True):
                api_delete(f"/documents/{document['id']}")
                st.rerun()

with tab_chat:
    st.subheader("Ask the knowledge base")
    selected_documents = st.multiselect("Limit to documents", options=list(document_options.keys()))
    selected_tags = st.text_input("Limit to tags", placeholder="policy, support")
    answer_format = st.selectbox("Response format", options=["default", "resume", "etapes", "risques", "faq"])

    if "question_input" not in st.session_state:
        st.session_state["question_input"] = ""

    quick_question_cols = st.columns(3)
    if quick_question_cols[0].button("Remote work policy", use_container_width=True):
        st.session_state["question_input"] = "What is the remote work policy?"
    if quick_question_cols[1].button("Incident escalation", use_container_width=True):
        st.session_state["question_input"] = "How should a severity one incident be escalated?"
    if quick_question_cols[2].button("Security rules", use_container_width=True):
        st.session_state["question_input"] = "What are the key rules for handling sensitive data?"

    question = st.text_area(
        "Question",
        key="question_input",
        placeholder="What is the onboarding policy for remote employees?",
    )

    if st.button("Ask", use_container_width=True, disabled=not question.strip() or not api_online):
        payload = {
            "question": question,
            "filters": {
                "document_ids": [document_options[name] for name in selected_documents],
                "tags": [tag.strip() for tag in selected_tags.split(",") if tag.strip()],
            },
            "answer_format": answer_format,
            "use_reranking": True,
        }
        with st.spinner("Generating answer..."):
            response = api_post("/query", json=payload)
        st.markdown("### Answer")
        st.write(response["answer"])
        st.caption(
            f"Latency: {response['latency_ms']} ms | Context chunks: {response['used_context_count']} | Status: {response['status']}"
        )
        st.markdown("### Sources")
        for source in response["sources"]:
            render_source(source)

    st.subheader("Compare two documents")
    left_document = st.selectbox("Left document", options=[""] + list(document_options.keys()), key="left_doc")
    right_document = st.selectbox("Right document", options=[""] + list(document_options.keys()), key="right_doc")
    compare_question = st.text_input("Comparison angle", placeholder="Compare incident escalation procedures")
    if st.button(
        "Compare",
        use_container_width=True,
        disabled=not left_document or not right_document or not compare_question.strip() or not api_online,
    ):
        payload = {
            "question": compare_question,
            "left_document_id": document_options[left_document],
            "right_document_id": document_options[right_document],
            "answer_format": "default",
        }
        with st.spinner("Comparing documents..."):
            response = api_post("/query/compare", json=payload)
        st.write(response["answer"])
        st.caption(f"Latency: {response['latency_ms']} ms")
        for source in response["sources"]:
            render_source(source)

    st.subheader("Recent history")
    for item in history:
        render_history_item(item)
