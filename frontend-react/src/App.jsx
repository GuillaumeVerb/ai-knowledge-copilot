import { useEffect, useState } from "react";
import { api } from "./api";

const quickQuestions = [
  { label: "Remote work", value: "What is the remote work policy?" },
  { label: "Escalation", value: "How should a severity one incident be escalated?" },
  { label: "Security", value: "What are the key rules for handling sensitive data?" },
  { label: "Onboarding", value: "What should new hires receive during onboarding?" },
];

const demoScenarios = [
  {
    title: "Grounded question",
    description: "Show concise retrieval with confidence and source excerpts in under 30 seconds.",
    actionLabel: "Load question",
    apply: ({ setQuestion, setSelectedTags, setAnswerFormat, setSelectedDocumentNames }) => {
      setQuestion("What is the remote work policy?");
      setSelectedTags("demo");
      setAnswerFormat("default");
      setSelectedDocumentNames([]);
    },
  },
  {
    title: "Procedure comparison",
    description: "Contrast two documents and show structured differences for incident handling.",
    actionLabel: "Load comparison",
    apply: ({ documents, setLeftDocument, setRightDocument, setCompareQuestion }) => {
      setCompareQuestion("Compare incident escalation procedures");
      setLeftDocument(findDocumentName(documents, ["product_guide"]));
      setRightDocument(findDocumentName(documents, ["support_procedure"]));
    },
  },
  {
    title: "Cross-doc synthesis",
    description: "Demonstrate multi-document reasoning while keeping the evidence perimeter visible.",
    actionLabel: "Load synthesis",
    apply: ({ documents, setSelectedSynthesisDocuments, setSynthesisQuestion }) => {
      setSynthesisQuestion("Summarize the main operational guidance across these documents");
      setSelectedSynthesisDocuments(findDocumentNames(documents, ["hr_handbook", "internal_policy", "support_procedure"]).slice(0, 3));
    },
  },
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
  const [notice, setNotice] = useState("");
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
  const latestDocuments = documents.filter((document) => document.is_latest_version);
  const documentMap = Object.fromEntries(documents.map((document) => [document.original_filename, document.id]));
  const activeResult = queryResult || compareResult || synthesisResult || summaryResult;

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

  function resetResults() {
    setQueryResult(null);
    setCompareResult(null);
    setSummaryResult(null);
    setSynthesisResult(null);
  }

  function onSuccess(message) {
    setNotice(message);
    setError("");
  }

  async function handleAsk() {
    try {
      setLoading(true);
      setNotice("");
      const result = await api.query({
        question,
        filters: {
          document_ids: selectedDocumentNames.map((name) => documentMap[name]).filter(Boolean),
          tags: selectedTags.split(",").map((tag) => tag.trim()).filter(Boolean),
        },
        answer_format: answerFormat,
        use_reranking: true,
      });
      setQueryResult(result);
      setCompareResult(null);
      setSummaryResult(null);
      setSynthesisResult(null);
      onSuccess("Grounded answer refreshed with the latest evidence set.");
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
      setNotice("");
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
      onSuccess("Comparison generated with structured differences and source support.");
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
      setNotice("");
      const result = await api.summarize(documentId);
      setSummaryResult(result);
      setQueryResult(null);
      setCompareResult(null);
      setSynthesisResult(null);
      onSuccess("Document summary updated with an explicit evidence perimeter.");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSynthesize() {
    try {
      setLoading(true);
      setNotice("");
      const result = await api.synthesize({
        question: synthesisQuestion,
        document_ids: selectedSynthesisDocuments.map((name) => documentMap[name]).filter(Boolean),
        answer_format: "resume",
      });
      setSynthesisResult(result);
      setQueryResult(null);
      setCompareResult(null);
      setSummaryResult(null);
      onSuccess("Synthesis generated across the selected document set.");
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
      setNotice("");
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
      onSuccess("Document uploaded and indexed successfully.");
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
      setNotice("");
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
      onSuccess("New document version created. Previous version remains traceable.");
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleAdminAction(action, successMessage) {
    try {
      setLoading(true);
      setNotice("");
      await action();
      onSuccess(successMessage);
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
      onSuccess(feedbackScore === 1 ? "Helpful feedback captured." : "Critical feedback captured.");
      await loadDashboard();
    } catch (err) {
      setError(err.message);
    }
  }

  function applyScenario(scenario) {
    scenario.apply({
      documents,
      setQuestion,
      setSelectedTags,
      setAnswerFormat,
      setSelectedDocumentNames,
      setLeftDocument,
      setRightDocument,
      setCompareQuestion,
      setSelectedSynthesisDocuments,
      setSynthesisQuestion,
    });
    resetResults();
    onSuccess(`Scenario ready: ${scenario.title}.`);
  }

  const activeFilterPills = buildFilterPills({
    selectedDocumentNames,
    selectedTags,
    answerFormat,
    leftDocument,
    rightDocument,
    selectedSynthesisDocuments,
    filterTag,
    filterStatus,
    filterSearch,
    filterCategory,
    filterDateFrom,
    filterDateTo,
    includeSuperseded,
  });

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-block accent">
          <p className="eyebrow dark">Demo readiness</p>
          <h2>Control room</h2>
          <p className="subtle">Use the React surface for interviews. Seed demo data, run one scenario, then open the evidence panel.</p>
          <div className="stack-actions">
            <button className="secondary-button" onClick={() => loadDashboard()}>Refresh dashboard</button>
            <button className="secondary-button" onClick={() => handleAdminAction(api.reindex, "Index refreshed from the current corpus.")} disabled={!health || loading}>
              Reindex corpus
            </button>
            <button className="secondary-button" onClick={() => handleAdminAction(api.seedDemo, "Demo dataset seeded or refreshed.")} disabled={!health || loading}>
              Seed demo dataset
            </button>
          </div>
        </div>

        <div className="sidebar-block">
          <h3>Runtime</h3>
          {health ? (
            <>
              <div className="status-pill success">Backend connected</div>
              <p>LLM mode: {health.llm_mode === "openai" ? "OpenAI production-grade" : "Local fallback"}</p>
              <p>Retrieval: {health.retrieval_mode}</p>
              <p>Supported files: {(health.supported_file_types || []).join(", ")}</p>
              {health.llm_mode !== "openai" && (
                <p className="subtle">Set `OPENAI_API_KEY` to upgrade answer quality. Local fallback remains useful for testing and evaluation.</p>
              )}
            </>
          ) : (
            <>
              <div className="status-pill danger">Backend unavailable</div>
              <p className="subtle">Expected API: {api.baseUrl}</p>
            </>
          )}
        </div>

        <div className="sidebar-block">
          <h3>Proof points</h3>
          <ul className="clean-list">
            <li>Grounded answers with explicit evidence perimeter</li>
            <li>Structured summary, compare, and synthesis workflows</li>
            <li>Confidence score, caution message, and traceable history</li>
            <li>Versioning and metadata-aware retrieval controls</li>
          </ul>
        </div>

        <div className="sidebar-block">
          <h3>Known limits</h3>
          <ul className="clean-list">
            <li>No OCR for scanned PDFs yet</li>
            <li>No auth, permissions, or external connectors in this iteration</li>
            <li>Best demo quality comes from OpenAI mode, not local fallback</li>
          </ul>
        </div>
      </aside>

      <main className="main">
        <section className="hero">
          <div className="hero-copy">
            <span className="eyebrow">Portfolio-ready internal knowledge copilot</span>
            <h1>Show retrieval quality, product thinking, and grounded AI behavior in one flow.</h1>
            <p>
              AI Knowledge Copilot turns internal documents into a demoable assistant with evidence-backed answers,
              structured outputs, operational workflows, and clear confidence signals.
            </p>
          </div>
          <div className="hero-grid">
            <article className="hero-card">
              <strong>Evidence-first answers</strong>
              <p>Every response surfaces source excerpts, document scope, and confidence reasoning.</p>
            </article>
            <article className="hero-card">
              <strong>Workflow depth</strong>
              <p>Ask, summarize, compare, synthesize, reimport, and review history from one UI.</p>
            </article>
            <article className="hero-card">
              <strong>Interview-ready story</strong>
              <p>Balanced polish for live demos, GitHub review, and architecture discussions.</p>
            </article>
          </div>
        </section>

        {error && <div className="error-banner">{error}</div>}
        {notice && <div className="notice-banner">{notice}</div>}

        <section className="metrics-grid">
          <article className="metric-card">
            <strong>{documents.length}</strong>
            <span>Documents available</span>
          </article>
          <article className="metric-card">
            <strong>{indexedCount}</strong>
            <span>Indexed and queryable</span>
          </article>
          <article className="metric-card">
            <strong>{history.length}</strong>
            <span>Recorded interactions</span>
          </article>
          <article className="metric-card">
            <strong>{health?.llm_mode === "openai" ? "OpenAI" : "Fallback"}</strong>
            <span>Current answer mode</span>
          </article>
        </section>

        <section className="scenario-grid">
          {demoScenarios.map((scenario) => (
            <article key={scenario.title} className="scenario-card">
              <p className="eyebrow dark">5-minute demo</p>
              <h3>{scenario.title}</h3>
              <p>{scenario.description}</p>
              <button className="ghost-button" onClick={() => applyScenario(scenario)}>
                {scenario.actionLabel}
              </button>
            </article>
          ))}
        </section>

        <section className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Knowledge workbench</h2>
                <span>Lead with one grounded answer, then branch into summary, compare, or synthesis.</span>
              </div>
              <div className="quick-actions">
                {quickQuestions.map((item) => (
                  <button key={item.label} className="chip" onClick={() => setQuestion(item.value)}>
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="workflow-grid">
              <section className="workflow-card">
                <div className="workflow-header">
                  <h3>Ask a question</h3>
                  <small>Best first move in a live demo</small>
                </div>
                <label>Limit to documents</label>
                <select
                  multiple
                  className="field multi"
                  value={selectedDocumentNames}
                  onChange={(event) => setSelectedDocumentNames(Array.from(event.target.selectedOptions).map((option) => option.value))}
                >
                  {latestDocuments.map((document) => (
                    <option key={document.id} value={document.original_filename}>
                      {document.original_filename}
                    </option>
                  ))}
                </select>

                <div className="field-row">
                  <div>
                    <label>Tags</label>
                    <input className="field" value={selectedTags} onChange={(e) => setSelectedTags(e.target.value)} placeholder="demo, policy, support" />
                  </div>
                  <div>
                    <label>Answer format</label>
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
                  {loading ? "Generating..." : "Generate grounded answer"}
                </button>
              </section>

              <section className="workflow-card">
                <div className="workflow-header">
                  <h3>Compare documents</h3>
                  <small>Useful for process alignment or policy drift</small>
                </div>
                <div className="field-row">
                  <select className="field" value={leftDocument} onChange={(e) => setLeftDocument(e.target.value)}>
                    <option value="">Left document</option>
                    {latestDocuments.map((document) => (
                      <option key={document.id} value={document.original_filename}>
                        {document.original_filename}
                      </option>
                    ))}
                  </select>
                  <select className="field" value={rightDocument} onChange={(e) => setRightDocument(e.target.value)}>
                    <option value="">Right document</option>
                    {latestDocuments.map((document) => (
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
                <button className="secondary-button" onClick={handleCompare} disabled={!health || loading || !leftDocument || !rightDocument || !compareQuestion.trim()}>
                  Build comparison
                </button>

                <div className="divider" />

                <div className="workflow-header">
                  <h3>Synthesize documents</h3>
                  <small>Show cross-document guidance with a bounded evidence set</small>
                </div>
                <label>Select documents</label>
                <select
                  multiple
                  className="field multi compact"
                  value={selectedSynthesisDocuments}
                  onChange={(event) => setSelectedSynthesisDocuments(Array.from(event.target.selectedOptions).map((option) => option.value))}
                >
                  {latestDocuments.map((document) => (
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
                <button className="secondary-button" onClick={handleSynthesize} disabled={!health || loading || selectedSynthesisDocuments.length < 2 || !synthesisQuestion.trim()}>
                  Build synthesis
                </button>
              </section>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Evidence panel</h2>
                <span>Answer, why it should be trusted, and exactly where it comes from.</span>
              </div>
            </div>

            {activeFilterPills.length > 0 && (
              <div className="pill-row">
                {activeFilterPills.map((pill) => (
                  <span key={pill} className="context-pill">{pill}</span>
                ))}
              </div>
            )}

            {queryResult && (
              <ResultCard
                result={queryResult}
                title="Grounded answer"
                feedbackState={feedbackState}
                onFeedback={handleFeedback}
              />
            )}

            {compareResult && (
              <ResultCard
                result={compareResult}
                title="Comparison output"
                comparison
                feedbackState={feedbackState}
                onFeedback={handleFeedback}
              />
            )}

            {synthesisResult && (
              <ResultCard
                result={synthesisResult}
                title="Synthesis output"
                feedbackState={feedbackState}
                onFeedback={handleFeedback}
              />
            )}

            {summaryResult && <SummaryCard result={summaryResult} />}

            {!activeResult && (
              <div className="empty-state">
                <strong>No result selected yet</strong>
                <p>Seed the dataset, load a scenario, then ask a question or summarize a document to populate this evidence panel.</p>
                <ul className="clean-list">
                  <li>Use the quick questions for a fast live demo</li>
                  <li>Highlight the confidence box and caution messaging</li>
                  <li>Open the source cards to show grounded excerpts</li>
                </ul>
              </div>
            )}
          </div>
        </section>

        <section className="content-grid lower">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Document library</h2>
                <span>Upload, filter, version, and summarize the current corpus.</span>
              </div>
            </div>

            <form className="upload-box" onSubmit={handleUpload}>
              <div className="box-header">
                <h3>Upload supported files</h3>
                <small>Accepted today: PDF, DOCX, TXT, MD, CSV</small>
              </div>
              <input type="file" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} />
              <div className="field-row">
                <input className="field" value={uploadTags} onChange={(e) => setUploadTags(e.target.value)} placeholder="demo, hr, onboarding" />
                <input className="field" value={uploadCategory} onChange={(e) => setUploadCategory(e.target.value)} placeholder="Category: HR, Security, Support" />
                <input className="field" type="date" value={uploadDate} onChange={(e) => setUploadDate(e.target.value)} />
              </div>
              <button className="secondary-button" disabled={!selectedFile || uploading || !health}>
                {uploading ? "Uploading..." : "Upload and index document"}
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
              <input className="field" value={filterSearch} onChange={(e) => setFilterSearch(e.target.value)} placeholder="Search by filename" />
            </div>
            <div className="field-row">
              <input className="field" type="date" value={filterDateFrom} onChange={(e) => setFilterDateFrom(e.target.value)} />
              <input className="field" type="date" value={filterDateTo} onChange={(e) => setFilterDateTo(e.target.value)} />
              <label className="toggle-field">
                <input type="checkbox" checked={includeSuperseded} onChange={(e) => setIncludeSuperseded(e.target.checked)} />
                <span>Include superseded versions</span>
              </label>
            </div>

            <form className="upload-box" onSubmit={handleReimport}>
              <div className="box-header">
                <h3>Create a new version</h3>
                <small>Use this in a demo to show lineage and latest-vs-superseded behavior.</small>
              </div>
              <div className="field-row">
                <select className="field" value={reimportTarget} onChange={(e) => setReimportTarget(e.target.value)}>
                  <option value="">Select base document</option>
                  {latestDocuments.map((document) => (
                    <option key={document.id} value={document.original_filename}>
                      {document.original_filename}
                    </option>
                  ))}
                </select>
                <input type="file" onChange={(event) => setReimportFile(event.target.files?.[0] || null)} />
              </div>
              <div className="field-row">
                <input className="field" value={reimportTags} onChange={(e) => setReimportTags(e.target.value)} placeholder="Optional new tags" />
                <input className="field" value={reimportCategory} onChange={(e) => setReimportCategory(e.target.value)} placeholder="Optional new category" />
                <input className="field" type="date" value={reimportDate} onChange={(e) => setReimportDate(e.target.value)} />
              </div>
              <button className="secondary-button" disabled={!reimportTarget || !reimportFile || uploading || !health}>
                {uploading ? "Creating version..." : "Create new version"}
              </button>
            </form>

            <div className="document-list">
              {documents.length === 0 && (
                <div className="empty-state">
                  <strong>No indexed documents yet</strong>
                  <p>Use the seed action for the recruiter demo, or upload a file manually to populate the library.</p>
                </div>
              )}

              {documents.map((document) => (
                <div key={document.id} className="document-card">
                  <div>
                    <strong>{document.original_filename}</strong>
                    <p>{document.status} · v{document.version_number}{document.is_latest_version ? " · latest" : " · superseded"}</p>
                    <p className="subtle">
                      {[document.category || "uncategorized", document.document_date, document.tags.join(", ") || "no tags"].filter(Boolean).join(" · ")}
                    </p>
                  </div>
                  <div className="document-actions">
                    <button className="ghost-button" onClick={() => handleSummary(document.id)}>Summary</button>
                    <button className="ghost-button danger" onClick={() => handleAdminAction(() => api.deleteDocument(document.id), "Document removed from the corpus.")}>
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Recent history</h2>
                <span>Traceability, latency, and captured feedback.</span>
              </div>
            </div>
            <div className="history-list">
              {history.length === 0 && (
                <div className="empty-state">
                  <strong>No history yet</strong>
                  <p>Run one query to show that answers are logged and reviewable.</p>
                </div>
              )}

              {history.map((item) => (
                <div key={item.id} className="history-card">
                  <strong>{item.question}</strong>
                  <p>{item.answer}</p>
                  <div className="badge-row">
                    <span className="badge">{item.latency_ms} ms</span>
                    <span className="badge">{item.sources_json.length} source(s)</span>
                    {item.feedback_score && (
                      <span className={`badge ${item.feedback_score > 0 ? "success-badge" : "danger-badge"}`}>
                        {item.feedback_score > 0 ? "helpful" : "not helpful"}
                      </span>
                    )}
                  </div>
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
        <div>
          <h3>{title}</h3>
          <p className="subtle">Designed for live review: answer, confidence, caution, and evidence perimeter.</p>
        </div>
        <div className="badge-row">
          <span className="badge">{result.status}</span>
          <span className={`badge confidence ${result.confidence_label || "low"}`}>
            {result.confidence_label || "low"} confidence
          </span>
          <span className="badge">{Math.round((result.confidence_score || 0) * 100)}%</span>
          <span className="badge">{result.used_context_count} source(s)</span>
          <span className="badge">{result.latency_ms} ms</span>
          {comparison && <span className="badge">comparison</span>}
        </div>
      </div>

      <div className="result-summary">
        <h4>Answer</h4>
        <p>{stripSourcesLine(result.answer)}</p>
      </div>

      <div className="evidence-overview">
        <div className="evidence-stat">
          <span>Evidence perimeter</span>
          <strong>{result.evidence_summary || `${result.sources?.length || 0} source excerpt(s)`}</strong>
        </div>
        <div className="evidence-stat">
          <span>Documents used</span>
          <strong>{result.evidence_documents?.length || uniqueDocumentNames(result.sources).length}</strong>
        </div>
        <div className="evidence-stat">
          <span>Confidence reason</span>
          <strong>{result.confidence_reason}</strong>
        </div>
      </div>

      {result.caution && (
        <div className="caution-box">
          <strong>Operator caution</strong>
          <p>{result.caution}</p>
        </div>
      )}

      {result.sections?.length > 0 && (
        <div className="section-stack">
          {result.sections.map((section) => (
            <details key={section.title} className="section-card" open={section.kind === "summary" || section.kind === "comparison"}>
              <summary>{section.title}</summary>
              {section.content && <p>{section.content}</p>}
              {section.items?.length > 0 && (
                <ul className="clean-list">
                  {section.items.map((item, index) => (
                    <li key={`${section.title}-${index}`}>{item}</li>
                  ))}
                </ul>
              )}
            </details>
          ))}
        </div>
      )}

      {result.sources?.length > 0 && (
        <div className="source-stack">
          {result.sources.map((source) => (
            <article key={source.chunk_id} className="source-card-react">
              <div className="source-header">
                <strong>{source.document_name}</strong>
                <small>
                  {source.page_number ? `page ${source.page_number}` : "document context"}
                  {source.score !== null && source.score !== undefined ? ` · score ${source.score.toFixed(2)}` : ""}
                </small>
              </div>
              {source.section_title && <p className="subtle">Section: {source.section_title}</p>}
              <p>{source.excerpt}</p>
            </article>
          ))}
        </div>
      )}

      {result.history_id && (
        <div className="feedback-row">
          <span>Was this useful?</span>
          <button className={`ghost-button ${currentFeedback === 1 ? "active" : ""}`} onClick={() => onFeedback(result.history_id, 1)}>
            Helpful
          </button>
          <button className={`ghost-button ${currentFeedback === -1 ? "active" : ""}`} onClick={() => onFeedback(result.history_id, -1)}>
            Not helpful
          </button>
        </div>
      )}
    </div>
  );
}

function SummaryCard({ result }) {
  return (
    <div className="result-card">
      <div className="result-header">
        <div>
          <h3>Document summary</h3>
          <p className="subtle">Single-document workflow with supporting evidence and structured recap.</p>
        </div>
        <div className="badge-row">
          <span className="badge">{result.latency_ms} ms</span>
          <span className="badge">{result.sources?.length || 0} source(s)</span>
        </div>
      </div>

      <div className="result-summary">
        <h4>Summary</h4>
        <p>{stripSourcesLine(result.summary)}</p>
      </div>

      <div className="evidence-overview">
        <div className="evidence-stat">
          <span>Evidence perimeter</span>
          <strong>{result.evidence_summary || `${result.sources?.length || 0} source excerpt(s)`}</strong>
        </div>
        <div className="evidence-stat">
          <span>Documents used</span>
          <strong>{result.evidence_documents?.length || uniqueDocumentNames(result.sources).length}</strong>
        </div>
      </div>

      <div className="section-stack">
        {result.sections?.map((section) => (
          <details key={section.title} className="section-card" open={section.kind === "summary"}>
            <summary>{section.title}</summary>
            {section.content && <p>{section.content}</p>}
            {section.items?.length > 0 && (
              <ul className="clean-list">
                {section.items.map((item, index) => (
                  <li key={`${section.title}-${index}`}>{item}</li>
                ))}
              </ul>
            )}
          </details>
        ))}
      </div>

      <div className="source-stack">
        {result.sources?.map((source) => (
          <article key={source.chunk_id} className="source-card-react">
            <div className="source-header">
              <strong>{source.document_name}</strong>
              <small>{source.page_number ? `page ${source.page_number}` : "document context"}</small>
            </div>
            <p>{source.excerpt}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function buildFilterPills(filters) {
  const pills = [];
  if (filters.selectedDocumentNames.length) pills.push(`Question scope: ${filters.selectedDocumentNames.length} selected document(s)`);
  if (filters.selectedTags.trim()) pills.push(`Question tags: ${filters.selectedTags}`);
  if (filters.answerFormat !== "default") pills.push(`Answer format: ${filters.answerFormat}`);
  if (filters.leftDocument && filters.rightDocument) pills.push(`Comparison: ${filters.leftDocument} vs ${filters.rightDocument}`);
  if (filters.selectedSynthesisDocuments.length >= 2) pills.push(`Synthesis scope: ${filters.selectedSynthesisDocuments.length} document(s)`);
  if (filters.filterTag) pills.push(`Library tag filter: ${filters.filterTag}`);
  if (filters.filterStatus) pills.push(`Library status: ${filters.filterStatus}`);
  if (filters.filterSearch) pills.push(`Library search: ${filters.filterSearch}`);
  if (filters.filterCategory) pills.push(`Library category: ${filters.filterCategory}`);
  if (filters.filterDateFrom || filters.filterDateTo) pills.push(`Library dates: ${filters.filterDateFrom || "start"} to ${filters.filterDateTo || "today"}`);
  if (!filters.includeSuperseded) pills.push("Latest versions only");
  return pills;
}

function stripSourcesLine(text = "") {
  return text.replace(/\n\s*Sources:\s.*$/s, "").trim();
}

function uniqueDocumentNames(sources = []) {
  return [...new Set((sources || []).map((source) => source.document_name))];
}

function findDocumentName(documents, keywords) {
  const match = documents.find((document) => keywords.every((keyword) => document.original_filename.toLowerCase().includes(keyword)));
  return match?.original_filename || "";
}

function findDocumentNames(documents, keywords) {
  return keywords
    .map((keyword) => findDocumentName(documents, [keyword]))
    .filter(Boolean);
}

export default App;
