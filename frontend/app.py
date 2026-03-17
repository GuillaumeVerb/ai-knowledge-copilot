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
                radial-gradient(circle at top left, rgba(244, 180, 0, 0.08), transparent 24%),
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.08), transparent 28%),
                linear-gradient(180deg, #f8fafc 0%, #edf4fb 100%);
        }
        .hero {
            padding: 1.5rem 1.6rem;
            border-radius: 26px;
            background: linear-gradient(135deg, #0b1220 0%, #12358a 55%, #3aa4e8 100%);
            color: white;
            box-shadow: 0 22px 60px rgba(15, 23, 42, 0.20);
            margin-bottom: 1rem;
        }
        .metric-card {
            padding: 1rem 1.05rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: 0 12px 30px rgba(148, 163, 184, 0.12);
        }
        .source-card {
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: #f8fafc;
            border-left: 4px solid #0ea5e9;
            margin-bottom: 0.8rem;
        }
        .feature-card {
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(148, 163, 184, 0.16);
            box-shadow: 0 10px 25px rgba(148, 163, 184, 0.10);
            min-height: 120px;
        }
        .result-shell {
            padding: 1rem 1.1rem;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.14);
            box-shadow: 0 12px 36px rgba(148, 163, 184, 0.12);
        }
        .mini-badge {
            display: inline-block;
            padding: 0.25rem 0.55rem;
            margin-right: 0.4rem;
            border-radius: 999px;
            background: #e2e8f0;
            color: #0f172a;
            font-size: 0.82rem;
            font-weight: 600;
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


def render_section(section: dict[str, Any]) -> None:
    title = section["title"]
    kind = section["kind"]
    content = section.get("content", "")
    items = section.get("items", [])
    with st.expander(title, expanded=kind in {"summary", "comparison"}):
        if content:
            if kind == "warning":
                st.warning(content)
            else:
                st.markdown(content)
        if items:
            if kind == "numbered":
                for index, item in enumerate(items, start=1):
                    st.markdown(f"{index}. {item}")
            else:
                for item in items:
                    st.markdown(f"- {item}")


def render_result(response: dict[str, Any], *, comparison: bool = False) -> None:
    title = "Comparison result" if comparison else "Answer"
    st.markdown(f"### {title}")
    if response["status"] == "not_found":
        st.warning(response["answer"])
        return

    st.markdown('<div class="result-shell">', unsafe_allow_html=True)
    badges = [
        f'<span class="mini-badge">{response["status"]}</span>',
        f'<span class="mini-badge">{response["used_context_count"]} source(s)</span>',
        f'<span class="mini-badge">{response["latency_ms"]} ms</span>',
    ]
    if comparison:
        badges.append('<span class="mini-badge">comparison</span>')
    st.markdown("".join(badges), unsafe_allow_html=True)

    if response.get("sections"):
        first_section = response["sections"][0]
        summary_content = first_section.get("content") or "\n".join(first_section.get("items", []))
        st.markdown(f"#### {first_section['title']}")
        st.write(summary_content)
        for section in response["sections"][1:]:
            render_section(section)
    else:
        st.write(response["answer"])

    if response.get("sources"):
        with st.expander("Sources", expanded=True):
            for source in response["sources"]:
                render_source(source)
    st.markdown("</div>", unsafe_allow_html=True)


def render_history_item(item: dict[str, Any]) -> None:
    with st.container(border=True):
        st.markdown(f"**Q:** {item['question']}")
        st.write(item["answer"])
        st.caption(f"Latency: {item['latency_ms']} ms")


def render_feature_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="feature-card">
            <strong>{title}</strong>
            <div style="margin-top:0.45rem;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""

health: dict[str, Any] = {}
api_online = False
try:
    health = api_get("/health")
    api_online = health.get("status") == "ok"
except Exception:
    health = {}
    api_online = False

documents = api_get("/documents") if api_online else []
history = api_get("/history") if api_online else []
document_options = {doc["original_filename"]: doc["id"] for doc in documents}
indexed_count = len([doc for doc in documents if doc["status"] == "indexed"])

st.markdown(
    """
    <div class="hero">
        <h1 style="margin:0 0 0.35rem 0;">AI Knowledge Copilot</h1>
        <p style="margin:0; font-size:1.02rem; max-width:860px;">
            Source-grounded search and synthesis for internal documentation, built to demonstrate retrieval quality,
            structured answers, and practical knowledge workflows.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

feature_cols = st.columns(3)
with feature_cols[0]:
    render_feature_card("Grounded answers", "Questions return concise answers with only the relevant supporting sources.")
with feature_cols[1]:
    render_feature_card("Structured summaries", "Document summaries are split into overview and key points for easier review.")
with feature_cols[2]:
    render_feature_card("Document comparison", "Compare procedures side by side with similarities, differences, and operational implications.")

with st.sidebar:
    st.subheader("Workspace")
    action_cols = st.columns(2)
    if action_cols[0].button("Refresh", use_container_width=True):
        st.rerun()

    if api_online:
        if action_cols[1].button("Reindex", use_container_width=True):
            api_post("/reindex")
            st.success("Index rebuilt.")
            st.rerun()
    else:
        action_cols[1].button("Reindex", disabled=True, use_container_width=True)

    if api_online:
        st.success("Backend connected")
        llm_mode = health.get("llm_mode", "unknown")
        retrieval_mode = health.get("retrieval_mode", "unknown")
        mode_label = "OpenAI production-grade" if llm_mode == "openai" else "Local fallback"
        st.caption(f"LLM mode: {mode_label}")
        st.caption(f"Retrieval: {retrieval_mode}")
        if llm_mode != "openai":
            st.info("Set `OPENAI_API_KEY` for the best demo quality.")
    else:
        st.error("Backend unavailable")
        st.caption("API base URL: " + API_BASE_URL)
        st.caption("Use `Refresh` after the backend finishes starting.")

    st.markdown("### Quick stats")
    st.metric("Documents", len(documents))
    st.metric("Indexed", indexed_count)
    st.metric("History entries", len(history))

    if api_online and st.button("Seed demo data", use_container_width=True):
        result = api_post("/demo/seed")
        st.success(f"Seeded {result['seeded']} docs, skipped {result['skipped']}.")
        st.rerun()

    st.markdown("### Demo scenarios")
    st.caption("HR policy lookup")
    st.caption("Incident escalation workflow")
    st.caption("Security policy guidance")
    st.caption("Procedure comparison")

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
    filter_bar = st.columns([2, 1, 2])
    filter_tag = filter_bar[0].text_input("Filter by tag", key="filter_tag")
    filter_status = filter_bar[1].selectbox("Status", options=["", "indexed", "processing", "failed"])
    search_query = filter_bar[2].text_input("Search document name")
    filtered_documents = (
        api_get("/documents", tag=filter_tag or None, status=filter_status or None, search=search_query or None)
        if api_online
        else []
    )
    if not filtered_documents:
        st.info("No documents imported yet.")
    for document in filtered_documents:
        with st.container(border=True):
            col1, col2, col3 = st.columns([5, 1.5, 1.5])
            col1.markdown(f"**{document['original_filename']}**")
            col1.caption(f"Status: {document['status']} | Tags: {', '.join(document['tags']) or 'none'}")
            if col2.button("Summary", key=f"summary_{document['id']}", use_container_width=True):
                summary = api_post(f"/documents/{document['id']}/summary")
                render_result(
                    {
                        "answer": summary["summary"],
                        "sections": summary.get("sections", []),
                        "sources": summary.get("sources", []),
                        "latency_ms": summary["latency_ms"],
                        "used_context_count": len(summary.get("sources", [])),
                        "status": "answered",
                    }
                )
            if col3.button("Delete", key=f"delete_{document['id']}", use_container_width=True):
                api_delete(f"/documents/{document['id']}")
                st.rerun()

with tab_chat:
    st.subheader("Ask the knowledge base")
    selected_documents = st.multiselect("Limit to documents", options=list(document_options.keys()))
    selected_tags = st.text_input("Limit to tags", placeholder="policy, support")
    answer_format = st.selectbox("Response format", options=["default", "resume", "etapes", "risques", "faq"])

    scenario_cols = st.columns(4)
    if scenario_cols[0].button("Remote work", use_container_width=True):
        st.session_state["question_input"] = "What is the remote work policy?"
    if scenario_cols[1].button("Escalation", use_container_width=True):
        st.session_state["question_input"] = "How should a severity one incident be escalated?"
    if scenario_cols[2].button("Security", use_container_width=True):
        st.session_state["question_input"] = "What are the key rules for handling sensitive data?"
    if scenario_cols[3].button("Onboarding", use_container_width=True):
        st.session_state["question_input"] = "What should new hires receive during onboarding?"

    question = st.text_area(
        "Question",
        key="question_input",
        placeholder="What is the onboarding policy for remote employees?",
        height=120,
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
        render_result(response)

    st.subheader("Compare two documents")
    compare_cols = st.columns(2)
    left_document = compare_cols[0].selectbox("Left document", options=[""] + list(document_options.keys()), key="left_doc")
    right_document = compare_cols[1].selectbox("Right document", options=[""] + list(document_options.keys()), key="right_doc")
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
        render_result(response, comparison=True)

    st.subheader("Recent history")
    for item in history:
        render_history_item(item)
