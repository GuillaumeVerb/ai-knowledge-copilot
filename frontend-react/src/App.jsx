import { useEffect, useState } from "react";
import { api } from "./api";

const quickQuestions = [
  { label: "Remote work", value: "What is the remote work policy?" },
  { label: "Escalation", value: "How should a severity one incident be escalated?" },
  { label: "Security", value: "What are the key rules for handling sensitive data?" },
  { label: "Onboarding", value: "What should new hires receive during onboarding?" },
];

function App() {
  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [history, setHistory] = useState([]);
  const [queryResult, setQueryResult] = useState(null);
  const [compareResult, setCompareResult] = useState(null);
  const [summaryResult, setSummaryResult] = useState(null);
  const [synthesisResult, setSynthesisResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [feedbackState, setFeedbackState] = useState({});
  const [question, setQuestion] = useState("What is the remote work policy?");
  const [selectedDocumentNames, setSelectedDocumentNames] = useState([]);
  const [selectedSynthesisDocuments, setSelectedSynthesisDocuments] = useState([]);
  const [selectedTags, setSelectedTags] = useState("");
  const [answerFormat, setAnswerFormat] = useState("default");
  const [leftDocument, setLeftDocument] = useState("");
  const [rightDocument, setRightDocument] = useState("");
  const [compareQuestion, setCompareQuestion] = useState("Compare incident escalation procedures");
  const [synthesisQuestion, setSynthesisQuestion] = useState("Summarize the main operational guidance across these documents");
  const [uploadTags, setUploadTags] = useState("");
  const [uploadCategory, setUploadCategory] = useState("");
  const [uploadDate, setUploadDate] = useState("");
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [filterTag, setFilterTag] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [filterSearch, setFilterSearch] = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [filterDateFrom, setFilterDateFrom] = useState("");
  const [filterDateTo, setFilterDateTo] = useState("");
  const [includeSuperseded, setIncludeSuperseded] = useState(true);
  const [reimportTarget, setReimportTarget] = useState("");
  const [reimportFile, setReimportFile] = useState(null);
  const [reimportCategory, setReimportCategory] = useState("");
  const [reimportDate, setReimportDate] = useState("");
  const [reimportTags, setReimportTags] = useState("");

  const indexedCount = documents.filter((document) => document.status === "indexed").length;
  const documentMap = Object.fromEntries(documents.map((document) => [document.original_filename, document.id]));

  async function loadDashboard() {
    try {
      const [healthData, documentsData, historyData] = await Promise.all([
        api.health(),
        api.documents({
          tag: filterTag,
          status: filterStatus,
          search: filterSearch,
          category: filterCategory,
          date_from: filterDateFrom,
          date_to: filterDateTo,
          include_superseded: includeSuperseded,
        }),
        api.history(),
      ]);
      setHealth(healthData);
      setDocuments(documentsData);
      setHistory(historyData);
      setError("");
    } catch (err) {
      setHealth(null);
      setError("Backend unavailable. Start the API and refresh.");
    }
  }

  useEffect(() => {
    loadDashboard();
  }, [filterTag, filterStatus, filterSearch, filterCategory, filterDateFrom, filterDateTo, includeSuperseded]);

  async function handleAsk() {
    try {
      setLoading(true);
      const payload = {
        question,
        filters: {
          document_ids: selectedDocumentNames.map((name) => documentMap[name]),
          tags: selectedTags.split(",").map((tag) => tag.trim()).filter(Boolean),
        },
        answer_format: answerFormat,
        use_reranking: true,
      };
      const result = await api.query(payload);
      setQueryResult(result);
      setCompareResult(null);
      setSummaryResult(null);
      setSynthesisResult(null);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCompare() {
    try {
      setLoading(true);
      const result = await api.compare({
        question: compareQuestion,
        left_document_id: documentMap[leftDocument],
        right_document_id: documentMap[rightDocument],
        answer_format: "default",
      });
      setCompareResult(result);
      setQueryResult(null);
      setSummaryResult(null);
      setSynthesisResult(null);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSummary(documentId) {
    try {
      setLoading(true);
      const result = await api.summarize(documentId);
      setSummaryResult(result);
      setQueryResult(null);
      setCompareResult(null);
      setSynthesisResult(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSynthesize() {
    try {
      setLoading(true);
      const result = await api.synthesize({
        question: synthesisQuestion,
        document_ids: selectedSynthesisDocuments.map((name) => documentMap[name]).filter(Boolean),
        answer_format: "resume",
      });
      setSynthesisResult(result);
      setQueryResult(null);
      setCompareResult(null);
      setSummaryResult(null);
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(event) {
    event.preventDefault();
    if (!selectedFile) return;
    try {
      setUploading(true);
      await api.upload({
        file: selectedFile,
        tags: uploadTags.split(",").map((tag) => tag.trim()).filter(Boolean),
        category: uploadCategory.trim(),
        documentDate: uploadDate || null,
      });
      setSelectedFile(null);
      setUploadTags("");
      setUploadCategory("");
      setUploadDate("");
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleReimport(event) {
    event.preventDefault();
    if (!reimportTarget || !reimportFile) return;
    try {
      setUploading(true);
      await api.reimportDocument({
        documentId: documentMap[reimportTarget],
        file: reimportFile,
        tags: reimportTags ? reimportTags.split(",").map((tag) => tag.trim()).filter(Boolean) : null,
        category: reimportCategory.trim(),
        documentDate: reimportDate || null,
      });
      setReimportTarget("");
      setReimportFile(null);
      setReimportCategory("");
      setReimportDate("");
      setReimportTags("");
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleAdminAction(action) {
    try {
      setLoading(true);
      await action();
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleFeedback(historyId, feedbackScore) {
    try {
      await api.feedback(historyId, { feedback_score: feedbackScore });
      setFeedbackState((current) => ({ ...current, [historyId]: feedbackScore }));
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-block">
          <h2>Control Room</h2>
          <button className="secondary-button" onClick={() => loadDashboard()}>Refresh</button>
          <button className="secondary-button" onClick={() => handleAdminAction(api.reindex)} disabled={!health}>
            Reindex
          </button>
          <button className="secondary-button" onClick={() => handleAdminAction(api.seedDemo)} disabled={!health}>
            Seed demo
          </button>
        </div>

        <div className="sidebar-block">
          <h3>Status</h3>
          {health ? (
            <>
              <div className="status-pill success">Backend connected</div>
              <p>LLM mode: {health.llm_mode === "openai" ? "OpenAI production-grade" : "Local fallback"}</p>
              <p>Retrieval: {health.retrieval_mode}</p>
              {health.llm_mode !== "openai" && <p className="subtle">Set `OPENAI_API_KEY` for the best demo quality.</p>}
            </>
          ) : (
            <>
              <div className="status-pill danger">Backend unavailable</div>
              <p className="subtle">Expected API: {api.baseUrl}</p>
            </>
          )}
        </div>

        <div className="sidebar-block">
          <h3>Stats</h3>
          <div className="mini-metric"><span>{documents.length}</span><small>documents</small></div>
          <div className="mini-metric"><span>{indexedCount}</span><small>indexed</small></div>
          <div className="mini-metric"><span>{history.length}</span><small>history entries</small></div>
        </div>

        <div className="sidebar-block">
          <h3>Scenarios</h3>
          <p className="subtle">HR policy lookup</p>
          <p className="subtle">Incident escalation workflow</p>
          <p className="subtle">Security guidance</p>
          <p className="subtle">Procedure comparison</p>
        </div>
      </aside>

      <main className="main">
        <section className="hero">
          <div>
            <h1>AI Knowledge Copilot</h1>
            <p>
              Source-grounded search and synthesis for internal documentation, designed to showcase
              retrieval quality, structured outputs, and practical knowledge workflows.
            </p>
          </div>
          <div className="hero-grid">
            <div className="hero-card">
              <strong>Grounded answers</strong>
              <p>Return concise answers with only the relevant supporting sources.</p>
            </div>
            <div className="hero-card">
              <strong>Structured summaries</strong>
              <p>Split one document into overview, key points, and evidence.</p>
            </div>
            <div className="hero-card">
              <strong>Comparison workflows</strong>
              <p>Surface similarities, differences, and operational implications.</p>
            </div>
          </div>
        </section>

        {error && <div className="error-banner">{error}</div>}

        <section className="metrics-grid">
          <article className="metric-card"><strong>{documents.length}</strong><span>Documents</span></article>
          <article className="metric-card"><strong>{indexedCount}</strong><span>Indexed</span></article>
          <article className="metric-card"><strong>{history.length}</strong><span>Recent queries</span></article>
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <h2>Knowledge chat</h2>
              <span>Ask, summarize, compare</span>
            </div>

            <div className="quick-actions">
              {quickQuestions.map((item) => (
                <button key={item.label} className="chip" onClick={() => setQuestion(item.value)}>
                  {item.label}
                </button>
              ))}
            </div>

            <label>Limit to documents</label>
            <select
              multiple
              className="field multi"
              value={selectedDocumentNames}
              onChange={(event) =>
                setSelectedDocumentNames(Array.from(event.target.selectedOptions).map((option) => option.value))
              }
            >
              {documents.map((document) => (
                <option key={document.id} value={document.original_filename}>
                  {document.original_filename}
                </option>
              ))}
            </select>

            <div className="field-row">
              <div>
                <label>Tags</label>
                <input className="field" value={selectedTags} onChange={(e) => setSelectedTags(e.target.value)} placeholder="policy, support" />
              </div>
              <div>
                <label>Format</label>
                <select className="field" value={answerFormat} onChange={(e) => setAnswerFormat(e.target.value)}>
                  <option value="default">default</option>
                  <option value="resume">resume</option>
                  <option value="etapes">etapes</option>
                  <option value="risques">risques</option>
                  <option value="faq">faq</option>
                </select>
              </div>
            </div>

            <label>Question</label>
            <textarea className="field textarea" value={question} onChange={(e) => setQuestion(e.target.value)} />
            <button className="primary-button" onClick={handleAsk} disabled={!health || loading || !question.trim()}>
              {loading ? "Generating..." : "Ask"}
            </button>

            <div className="compare-box">
              <h3>Compare documents</h3>
              <div className="field-row">
                <select className="field" value={leftDocument} onChange={(e) => setLeftDocument(e.target.value)}>
                  <option value="">Left document</option>
                  {documents.map((document) => (
                    <option key={document.id} value={document.original_filename}>
                      {document.original_filename}
                    </option>
                  ))}
                </select>
                <select className="field" value={rightDocument} onChange={(e) => setRightDocument(e.target.value)}>
                  <option value="">Right document</option>
                  {documents.map((document) => (
                    <option key={document.id} value={document.original_filename}>
                      {document.original_filename}
                    </option>
                  ))}
                </select>
              </div>
              <input
                className="field"
                value={compareQuestion}
                onChange={(e) => setCompareQuestion(e.target.value)}
                placeholder="Compare incident escalation procedures"
              />
              <button
                className="secondary-button"
                onClick={handleCompare}
                disabled={!health || loading || !leftDocument || !rightDocument || !compareQuestion.trim()}
              >
                Compare
              </button>
            </div>

            <div className="compare-box">
              <h3>Synthesize multiple documents</h3>
              <label>Select documents</label>
              <select
                multiple
                className="field multi"
                value={selectedSynthesisDocuments}
                onChange={(event) =>
                  setSelectedSynthesisDocuments(Array.from(event.target.selectedOptions).map((option) => option.value))
                }
              >
                {documents.map((document) => (
                  <option key={document.id} value={document.original_filename}>
                    {document.original_filename}
                  </option>
                ))}
              </select>
              <input
                className="field"
                value={synthesisQuestion}
                onChange={(e) => setSynthesisQuestion(e.target.value)}
                placeholder="Summarize the main operational guidance across these documents"
              />
              <button
                className="secondary-button"
                onClick={handleSynthesize}
                disabled={!health || loading || selectedSynthesisDocuments.length < 2 || !synthesisQuestion.trim()}
              >
                Synthesize
              </button>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>Results</h2>
              <span>Structured output</span>
            </div>
            {queryResult && <ResultCard result={queryResult} title="Answer" feedbackState={feedbackState} onFeedback={handleFeedback} />}
            {compareResult && <ResultCard result={compareResult} title="Comparison" comparison feedbackState={feedbackState} onFeedback={handleFeedback} />}
            {synthesisResult && <ResultCard result={synthesisResult} title="Synthesis" feedbackState={feedbackState} onFeedback={handleFeedback} />}
            {summaryResult && (
              <ResultCard
                result={{
                  answer: summaryResult.summary,
                  sections: summaryResult.sections,
                  sources: summaryResult.sources,
                  latency_ms: summaryResult.latency_ms,
                  used_context_count: summaryResult.sources.length,
                  status: "answered",
                  confidence_label: "medium",
                  confidence_reason: "Summary grounded in the selected document chunks.",
                }}
                title="Summary"
                feedbackState={feedbackState}
                onFeedback={handleFeedback}
              />
            )}
            {!queryResult && !compareResult && !summaryResult && !synthesisResult && (
              <div className="empty-state">
                <strong>No result yet</strong>
                <p>Ask a question, summarize a document, or compare two procedures to generate a demo output.</p>
              </div>
            )}
          </div>
        </section>

        <section className="content-grid lower">
          <div className="panel">
            <div className="panel-header">
              <h2>Document library</h2>
              <span>Upload and review</span>
            </div>

            <form className="upload-box" onSubmit={handleUpload}>
              <input type="file" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} />
              <div className="field-row">
                <input
                  className="field"
                  value={uploadTags}
                  onChange={(e) => setUploadTags(e.target.value)}
                  placeholder="hr, onboarding"
                />
                <input
                  className="field"
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  placeholder="Category: HR, Security, Support"
                />
                <input
                  className="field"
                  type="date"
                  value={uploadDate}
                  onChange={(e) => setUploadDate(e.target.value)}
                />
              </div>
              <button className="secondary-button" disabled={!selectedFile || uploading || !health}>
                {uploading ? "Uploading..." : "Upload document"}
              </button>
            </form>

            <div className="field-row">
              <input className="field" value={filterTag} onChange={(e) => setFilterTag(e.target.value)} placeholder="Filter by tag" />
              <select className="field" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                <option value="">All status</option>
                <option value="indexed">indexed</option>
                <option value="processing">processing</option>
                <option value="failed">failed</option>
              </select>
              <input className="field" value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)} placeholder="Category" />
              <input className="field" value={filterSearch} onChange={(e) => setFilterSearch(e.target.value)} placeholder="Search name" />
            </div>
            <div className="field-row">
              <input className="field" type="date" value={filterDateFrom} onChange={(e) => setFilterDateFrom(e.target.value)} />
              <input className="field" type="date" value={filterDateTo} onChange={(e) => setFilterDateTo(e.target.value)} />
              <label className="toggle-field">
                <input type="checkbox" checked={includeSuperseded} onChange={(e) => setIncludeSuperseded(e.target.checked)} />
                <span>Show previous versions</span>
              </label>
            </div>

            <form className="upload-box" onSubmit={handleReimport}>
              <h3>Reimport as new version</h3>
              <div className="field-row">
                <select className="field" value={reimportTarget} onChange={(e) => setReimportTarget(e.target.value)}>
                  <option value="">Select base document</option>
                  {documents.filter((document) => document.is_latest_version).map((document) => (
                    <option key={document.id} value={document.original_filename}>
                      {document.original_filename}
                    </option>
                  ))}
                </select>
                <input type="file" onChange={(event) => setReimportFile(event.target.files?.[0] || null)} />
              </div>
              <div className="field-row">
                <input
                  className="field"
                  value={reimportTags}
                  onChange={(e) => setReimportTags(e.target.value)}
                  placeholder="Optional new tags"
                />
                <input
                  className="field"
                  value={reimportCategory}
                  onChange={(e) => setReimportCategory(e.target.value)}
                  placeholder="Optional new category"
                />
                <input className="field" type="date" value={reimportDate} onChange={(e) => setReimportDate(e.target.value)} />
              </div>
              <button className="secondary-button" disabled={!reimportTarget || !reimportFile || uploading || !health}>
                {uploading ? "Creating version..." : "Create new version"}
              </button>
            </form>

            <div className="document-list">
              {documents.map((document) => (
                <div key={document.id} className="document-card">
                  <div>
                    <strong>{document.original_filename}</strong>
                    <p>
                      {document.status} · v{document.version_number}
                      {document.is_latest_version ? " · latest" : " · superseded"}
                    </p>
                    <p className="subtle">
                      {[document.category, document.document_date, document.tags.join(", ") || "no tags"].filter(Boolean).join(" · ")}
                    </p>
                  </div>
                  <div className="document-actions">
                    <button className="ghost-button" onClick={() => handleSummary(document.id)}>Summary</button>
                    <button className="ghost-button danger" onClick={() => handleAdminAction(() => api.deleteDocument(document.id))}>
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>Recent history</h2>
              <span>Traceability</span>
            </div>
            <div className="history-list">
              {history.map((item) => (
                <div key={item.id} className="history-card">
                  <strong>{item.question}</strong>
                  <p>{item.answer}</p>
                  <small>{item.latency_ms} ms</small>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

function ResultCard({ result, title, comparison = false, feedbackState = {}, onFeedback }) {
  const currentFeedback = result.history_id ? feedbackState[result.history_id] : null;
  return (
    <div className="result-card">
      <div className="result-header">
        <h3>{title}</h3>
        <div className="badge-row">
          <span className="badge">{result.status}</span>
          <span className={`badge confidence ${result.confidence_label || "low"}`}>
            {result.confidence_label || "low"} confidence
          </span>
          <span className="badge">{result.used_context_count} source(s)</span>
          <span className="badge">{result.latency_ms} ms</span>
          {comparison && <span className="badge">comparison</span>}
        </div>
      </div>

      {result.confidence_reason && (
        <div className="confidence-box">
          <strong>Why this answer</strong>
          <p>{result.confidence_reason}</p>
        </div>
      )}

      {result.sections?.length ? (
        <>
          <div className="result-summary">
            <h4>{result.sections[0].title}</h4>
            <p>{result.sections[0].content || result.sections[0].items?.join(" ")}</p>
          </div>
          {result.sections.slice(1).map((section) => (
            <details key={section.title} className="section-card" open={section.kind === "comparison"}>
              <summary>{section.title}</summary>
              {section.content && <p>{section.content}</p>}
              {section.items?.length > 0 && (
                <ul>
                  {section.items.map((item, index) => (
                    <li key={`${section.title}-${index}`}>{item}</li>
                  ))}
                </ul>
              )}
            </details>
          ))}
        </>
      ) : (
        <p>{result.answer}</p>
      )}

      {result.sources?.length > 0 && (
        <details className="section-card" open>
          <summary>Sources</summary>
          {result.sources.map((source) => (
            <div key={source.chunk_id} className="source-card-react">
              <strong>{source.document_name}</strong>
              <small>{source.page_number ? `page ${source.page_number}` : "document context"}</small>
              <p>{source.excerpt}</p>
            </div>
          ))}
        </details>
      )}

      {result.history_id && (
        <div className="feedback-row">
          <span>Was this useful?</span>
          <button
            className={`ghost-button ${currentFeedback === 1 ? "active" : ""}`}
            onClick={() => onFeedback(result.history_id, 1)}
          >
            Helpful
          </button>
          <button
            className={`ghost-button ${currentFeedback === -1 ? "active" : ""}`}
            onClick={() => onFeedback(result.history_id, -1)}
          >
            Not helpful
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
