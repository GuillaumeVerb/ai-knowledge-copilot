import { useEffect, useState } from "react";
import { api } from "./api";

const COPY = {
  fr: {
    appName: "Copilote IA documentaire",
    heroTitle: "Copilote IA documentaire",
    heroSubtitle: "Interrogez vos documents, comparez vos procédures et obtenez des réponses fiables avec sources",
    heroDescription:
      "Un assistant IA interne conçu pour les équipes RH, support et opérations. Réduit le temps de recherche, standardise les réponses et garantit des réponses basées sur des documents réels.",
    nav: ["Documents", "Historique", "Cas d’usage", "Paramètres"],
    ask: "Question",
    compare: "Comparer",
    synthesize: "Synthèse",
    evidence: "Preuves",
    trust: "Confiance",
    explanation: "Explication",
    useCasesTitle: "Pour qui ?",
    impactTitle: "Impact métier",
    useCases: [
      ["RH", "Politiques internes, onboarding et réponses homogènes aux questions récurrentes."],
      ["Support", "FAQ, procédures d’incident et réponses standardisées aux tickets."],
      ["Conseil", "Rapports, synthèses multi-documents et accélération des missions."],
      ["Opérations", "Procédures, runbooks et alignement sur les bonnes versions."],
    ],
    impact: [
      "Réduction du temps de recherche",
      "Réponses standardisées",
      "Meilleure diffusion des connaissances",
      "IA fiable avec preuves visibles",
    ],
    tabsTitle: "Flux de travail",
    resultTitle: "Réponse structurée",
    docLibrary: "Bibliothèque documentaire",
    reviewHistory: "Historique de revue",
    upload: "Ajouter un document",
    uploadHint: "PDF, DOCX, TXT, MD, CSV. Métadonnées métier incluses.",
    titleLabel: "Titre",
    categoryLabel: "Catégorie",
    versionLabel: "Version",
    tagsLabel: "Tags",
    questionLabel: "Question utilisateur",
    formatLabel: "Format de réponse",
    scopeLabel: "Limiter à certains documents",
    compareLeft: "Document A",
    compareRight: "Document B",
    synthDocs: "Documents à synthétiser",
    askButton: "Obtenir une réponse fondée",
    compareButton: "Comparer les documents",
    synthButton: "Créer une synthèse",
    summaryButton: "Résumer",
    deleteButton: "Supprimer",
    exportButton: "Exporter",
    shareButton: "Lien partageable",
    exportSoon: "Bientôt",
    sourcePanelEmpty: "Lancez une question, une comparaison ou une synthèse pour afficher les preuves et le niveau de confiance.",
    noReliableAnswer: "Je ne sais pas sur la base des documents disponibles.",
    askHint: "Exemple : Quelle est la politique de télétravail pour les nouveaux arrivants ?",
    compareHint: "Exemple : Compare les procédures d’escalade entre les deux runbooks.",
    synthHint: "Exemple : Fais une synthèse des directives RH à partager aux managers.",
    why: "Pourquoi cette réponse ?",
    selectedDocs: "Documents utilisés",
    coverage: "Couverture",
    selectedBecause: "Pourquoi sélectionnés",
    suggestions: "Suggestions",
    suggestedQuestions: "Questions suggérées",
    filtersHint: "Souhaitez-vous limiter aux documents RH ?",
    placeholders: {
      title: "Ex. Politique RH 2026",
      category: "RH, Support, Conseil, Opérations",
      version: "v2026.1",
      tags: "rh, onboarding, politique",
      search: "Rechercher un document",
      filter: "Filtrer par catégorie",
      compare: "Comparer les différences clés et les impacts opérationnels",
      synth: "Résumer les points communs et différences majeures",
    },
    status: {
      grounded: "Fondée",
      limited: "Limitée",
      none: "Aucune réponse fiable",
      high: "Élevée",
      medium: "Moyenne",
      low: "Faible",
    },
    runtimeConnected: "Backend connecté",
    runtimeUnavailable: "Backend indisponible",
    records: "interactions récentes",
    latestOnly: "Dernières versions seulement",
    language: "Langue",
    modeAuto: "Détection auto",
    confidenceLine: "Confiance",
    safetyLine: "Sécurité",
    explanationLine: "Niveau de couverture et justification de sélection des sources",
    historyEmpty: "Aucune interaction enregistrée pour le moment.",
    documentsEmpty: "Aucun document indexé pour le moment.",
    settingsTitle: "Paramètres produit",
    integrations: "Intégrations",
    integrationsHint: "Slack et Notion disponibles prochainement.",
    darkMode: "Mode sombre",
  },
  en: {
    appName: "Document AI Copilot",
    heroTitle: "Document AI Copilot",
    heroSubtitle: "Query your documents, compare procedures, and get reliable answers with sources",
    heroDescription:
      "An internal AI assistant for HR, support, and operations teams. It reduces search time, standardizes answers, and keeps responses grounded in real documents.",
    nav: ["Documents", "History", "Use Cases", "Settings"],
    ask: "Ask",
    compare: "Compare",
    synthesize: "Synthesis",
    evidence: "Evidence",
    trust: "Confidence",
    explanation: "Explanation",
    useCasesTitle: "Who is it for?",
    impactTitle: "Business impact",
    useCases: [
      ["HR", "Policies, onboarding, and consistent answers for recurring employee questions."],
      ["Support", "FAQs, incident procedures, and standardized ticket responses."],
      ["Consulting", "Reports, multi-document synthesis, and faster client delivery."],
      ["Operations", "Procedures, runbooks, and version-safe operational guidance."],
    ],
    impact: [
      "Reduced search time",
      "Standardized answers",
      "Better knowledge distribution",
      "Reliable AI with visible evidence",
    ],
    tabsTitle: "Workflows",
    resultTitle: "Structured answer",
    docLibrary: "Document library",
    reviewHistory: "Review history",
    upload: "Upload document",
    uploadHint: "PDF, DOCX, TXT, MD, CSV with business metadata.",
    titleLabel: "Title",
    categoryLabel: "Category",
    versionLabel: "Version",
    tagsLabel: "Tags",
    questionLabel: "User question",
    formatLabel: "Answer format",
    scopeLabel: "Limit to documents",
    compareLeft: "Document A",
    compareRight: "Document B",
    synthDocs: "Documents to synthesize",
    askButton: "Get grounded answer",
    compareButton: "Compare documents",
    synthButton: "Create synthesis",
    summaryButton: "Summarize",
    deleteButton: "Delete",
    exportButton: "Export",
    shareButton: "Shareable link",
    exportSoon: "Soon",
    sourcePanelEmpty: "Run a question, comparison, or synthesis to display evidence and trust signals.",
    noReliableAnswer: "I don't know based on available documents.",
    askHint: "Example: What is the remote work policy for new hires?",
    compareHint: "Example: Compare escalation procedures between the two runbooks.",
    synthHint: "Example: Summarize the main HR guidance to share with managers.",
    why: "Why this answer?",
    selectedDocs: "Documents used",
    coverage: "Coverage",
    selectedBecause: "Why selected",
    suggestions: "Suggestions",
    suggestedQuestions: "Suggested questions",
    filtersHint: "Do you want HR documents only?",
    placeholders: {
      title: "Ex. HR Policy 2026",
      category: "HR, Support, Consulting, Operations",
      version: "v2026.1",
      tags: "hr, onboarding, policy",
      search: "Search documents",
      filter: "Filter by category",
      compare: "Compare key differences and operational impacts",
      synth: "Summarize common themes and key differences",
    },
    status: {
      grounded: "Grounded",
      limited: "Limited",
      none: "No reliable answer",
      high: "High",
      medium: "Medium",
      low: "Low",
    },
    runtimeConnected: "Backend connected",
    runtimeUnavailable: "Backend unavailable",
    records: "recent interactions",
    latestOnly: "Latest versions only",
    language: "Language",
    modeAuto: "Auto detect",
    confidenceLine: "Confidence",
    safetyLine: "Safety",
    explanationLine: "Coverage level and rationale for source selection",
    historyEmpty: "No recorded interactions yet.",
    documentsEmpty: "No indexed documents yet.",
    settingsTitle: "Product settings",
    integrations: "Integrations",
    integrationsHint: "Slack and Notion placeholders available next.",
    darkMode: "Dark mode",
  },
};

const ANSWER_FORMATS = [
  { value: "concise", fr: "Réponse concise", en: "Concise answer" },
  { value: "detailed", fr: "Réponse détaillée", en: "Detailed answer" },
  { value: "checklist", fr: "Checklist", en: "Checklist" },
  { value: "comparison", fr: "Comparaison", en: "Comparison" },
  { value: "summary", fr: "Résumé", en: "Summary" },
];

const FOLLOW_UPS = {
  fr: [
    "Quelles pièces justificatives dois-je transmettre ?",
    "Peux-tu comparer cette procédure avec la version précédente ?",
    "Résume-moi les exceptions importantes pour les managers.",
  ],
  en: [
    "Which supporting documents should I share?",
    "Can you compare this procedure with the previous version?",
    "Summarize the important exceptions for managers.",
  ],
};

function App() {
  const [language, setLanguage] = useState("fr");
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState("ask");
  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [history, setHistory] = useState([]);
  const [result, setResult] = useState(null);
  const [activeSourceId, setActiveSourceId] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [question, setQuestion] = useState("Quelle est la politique de télétravail ?");
  const [answerFormat, setAnswerFormat] = useState("concise");
  const [selectedDocumentIds, setSelectedDocumentIds] = useState([]);
  const [selectedTags, setSelectedTags] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [compareQuestion, setCompareQuestion] = useState("Compare les procédures d’escalade et les impacts opérationnels.");
  const [leftDocumentId, setLeftDocumentId] = useState("");
  const [rightDocumentId, setRightDocumentId] = useState("");
  const [synthesisQuestion, setSynthesisQuestion] = useState("Fais une synthèse des principaux éléments à retenir.");
  const [synthesisDocumentIds, setSynthesisDocumentIds] = useState([]);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadCategory, setUploadCategory] = useState("");
  const [uploadVersion, setUploadVersion] = useState("");
  const [uploadTags, setUploadTags] = useState("");
  const [uploadDate, setUploadDate] = useState("");
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [latestOnly, setLatestOnly] = useState(false);
  const [conversationMemory, setConversationMemory] = useState([]);

  const t = COPY[language];
  const latestDocuments = documents.filter((item) => (latestOnly ? item.is_latest_version : true));
  const indexedDocuments = documents.filter((item) => item.status === "indexed");
  const displayedDocuments = latestDocuments.filter((item) => {
    const matchesSearch =
      !search ||
      item.original_filename.toLowerCase().includes(search.toLowerCase()) ||
      (item.title || "").toLowerCase().includes(search.toLowerCase());
    const matchesCategory = !categoryFilter || (item.category || "").toLowerCase().includes(categoryFilter.toLowerCase());
    return matchesSearch && matchesCategory;
  });
  const uniqueDocs = [...new Set((result?.sources || []).map((source) => source.document_name))];

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? "dark" : "light";
  }, [darkMode]);

  useEffect(() => {
    loadApp();
  }, [latestOnly]);

  async function loadApp() {
    try {
      const [healthData, docs, historyData] = await Promise.all([
        api.health(),
        api.documents({ include_superseded: !latestOnly }),
        api.history(),
      ]);
      setHealth(healthData);
      setDocuments(docs);
      setHistory(historyData);
      setError("");
    } catch (err) {
      setError(err.message);
      setHealth(null);
    }
  }

  function rememberInteraction(questionText, payload) {
    setConversationMemory((current) =>
      [...current, { question: questionText, answer: payload.answer || payload.summary || "" }].slice(-6),
    );
  }

  function normalizeTags(value) {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  async function handleAsk() {
    try {
      setLoading(true);
      const payload = await api.query({
        question,
        filters: {
          document_ids: selectedDocumentIds,
          tags: normalizeTags(selectedTags),
          categories: selectedCategory ? [selectedCategory] : [],
        },
        answer_format: answerFormat,
        language: "auto",
        conversation_history: conversationMemory,
        use_reranking: true,
      });
      setResult({ ...payload, mode: "ask" });
      rememberInteraction(question, payload);
      setNotice(language === "fr" ? "Réponse mise à jour avec preuves visibles." : "Answer refreshed with visible evidence.");
      setActiveTab("ask");
      await loadApp();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCompare() {
    try {
      setLoading(true);
      const payload = await api.compare({
        question: compareQuestion,
        left_document_id: leftDocumentId,
        right_document_id: rightDocumentId,
        language: "auto",
        conversation_history: conversationMemory,
        answer_format: "comparison",
      });
      setResult({ ...payload, mode: "compare" });
      rememberInteraction(compareQuestion, payload);
      setNotice(language === "fr" ? "Comparaison générée avec impacts opérationnels." : "Comparison generated with operational impacts.");
      setActiveTab("compare");
      await loadApp();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSynthesis() {
    try {
      setLoading(true);
      const payload = await api.synthesize({
        question: synthesisQuestion,
        document_ids: synthesisDocumentIds,
        answer_format: "summary",
        language: "auto",
        conversation_history: conversationMemory,
      });
      setResult({ ...payload, mode: "synthesize" });
      rememberInteraction(synthesisQuestion, payload);
      setNotice(language === "fr" ? "Synthèse créée avec regroupement thématique." : "Synthesis created with grouped themes.");
      setActiveTab("synthesize");
      await loadApp();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSummary(documentId, label) {
    try {
      setLoading(true);
      const payload = await api.summarize(documentId);
      setResult({
        answer: payload.summary,
        sources: payload.sources,
        sections: payload.sections,
        evidence_summary: payload.evidence_summary,
        evidence_documents: payload.evidence_documents,
        confidence: "Medium",
        confidence_label: "medium",
        confidence_reason: language === "fr" ? "Résumé mono-document avec preuves sélectionnées." : "Single-document summary with selected evidence.",
        safety: "Grounded",
        suggestions: language === "fr" ? ["Comparer avec une version précédente.", "Partager ce résumé avec l’équipe."] : ["Compare with a previous version.", "Share this summary with the team."],
        used_context_count: payload.sources?.length || 0,
        latency_ms: payload.latency_ms,
        status: "answered",
        mode: "summary",
        detected_language: language,
      });
      setNotice(
        language === "fr"
          ? `Résumé généré pour ${label}.`
          : `Summary generated for ${label}.`,
      );
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
        tags: normalizeTags(uploadTags),
        title: uploadTitle,
        category: uploadCategory,
        documentDate: uploadDate || null,
        version: uploadVersion,
      });
      setSelectedFile(null);
      setUploadTitle("");
      setUploadCategory("");
      setUploadVersion("");
      setUploadTags("");
      setUploadDate("");
      setNotice(language === "fr" ? "Document indexé avec succès." : "Document indexed successfully.");
      await loadApp();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(documentId) {
    try {
      await api.deleteDocument(documentId);
      setNotice(language === "fr" ? "Document supprimé du corpus." : "Document removed from the corpus.");
      await loadApp();
    } catch (err) {
      setError(err.message);
    }
  }

  function scrollToDocument(name) {
    const target = document.getElementById(`doc-${name}`);
    target?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  return (
    <div className="v3-shell">
      <aside className="left-rail">
        <div className="brand-card">
          <div className="brand-mark">AI</div>
          <div>
            <div className="brand-name">{t.appName}</div>
            <small>{health ? t.runtimeConnected : t.runtimeUnavailable}</small>
          </div>
        </div>

        <nav className="nav-card">
          {t.nav.map((item) => (
            <a key={item} href={`#${slugify(item)}`} className="nav-link">
              {item}
            </a>
          ))}
        </nav>

        <section className="rail-card">
          <h3>{t.settingsTitle}</h3>
          <div className="toggle-row">
            <span>{t.language}</span>
            <div className="segmented">
              <button className={language === "fr" ? "active" : ""} onClick={() => setLanguage("fr")}>FR</button>
              <button className={language === "en" ? "active" : ""} onClick={() => setLanguage("en")}>EN</button>
            </div>
          </div>
          <label className="toggle-check">
            <input type="checkbox" checked={darkMode} onChange={(event) => setDarkMode(event.target.checked)} />
            <span>{t.darkMode}</span>
          </label>
          <div className="runtime-box">
            <strong>{health?.llm_mode === "openai" ? "OpenAI" : "Fallback"}</strong>
            <small>{health?.retrieval_mode || api.baseUrl}</small>
          </div>
        </section>

        <section className="rail-card" id="cas-dusage">
          <h3>{t.useCasesTitle}</h3>
          <ul className="plain-list compact">
            {t.useCases.map(([label]) => (
              <li key={label}>{label}</li>
            ))}
          </ul>
        </section>

        <section className="rail-card">
          <h3>{t.integrations}</h3>
          <p>{t.integrationsHint}</p>
          <div className="pill-row">
            <span className="soft-pill">Slack</span>
            <span className="soft-pill">Notion</span>
            <span className="soft-pill">{t.exportSoon}</span>
          </div>
        </section>
      </aside>

      <main className="center-panel">
        <section className="hero-card-v3">
          <div>
            <span className="eyebrow">{language === "fr" ? "Assistant interne de confiance" : "Trusted internal assistant"}</span>
            <h1>{t.heroTitle}</h1>
            <h2>{t.heroSubtitle}</h2>
            <p>{t.heroDescription}</p>
          </div>
          <div className="hero-metrics">
            <Metric value={indexedDocuments.length} label={language === "fr" ? "documents indexés" : "indexed documents"} />
            <Metric value={history.length} label={t.records} />
            <Metric value={health?.llm_mode === "openai" ? "OpenAI" : "Fallback"} label="runtime" />
          </div>
        </section>

        {error && <div className="banner error">{error}</div>}
        {notice && <div className="banner success">{notice}</div>}

        <section className="dual-grid" id="cas-dusage">
          <InfoSection title={t.useCasesTitle} items={t.useCases} rich />
          <InfoSection title={t.impactTitle} items={t.impact.map((item) => [item, ""])} />
        </section>

        <section className="workspace-card">
          <div className="workspace-head">
            <div>
              <span className="eyebrow muted">{t.tabsTitle}</span>
              <h3>{language === "fr" ? "Assistant orienté tâches" : "Task-oriented assistant"}</h3>
            </div>
            <div className="tab-switch">
              <button className={activeTab === "ask" ? "active" : ""} onClick={() => setActiveTab("ask")}>{t.ask}</button>
              <button className={activeTab === "compare" ? "active" : ""} onClick={() => setActiveTab("compare")}>{t.compare}</button>
              <button className={activeTab === "synthesize" ? "active" : ""} onClick={() => setActiveTab("synthesize")}>{t.synthesize}</button>
            </div>
          </div>

          {activeTab === "ask" && (
            <div className="workflow-form">
              <div className="field-grid">
                <label>
                  <span>{t.scopeLabel}</span>
                  <select multiple value={selectedDocumentIds} onChange={(event) => setSelectedDocumentIds(Array.from(event.target.selectedOptions).map((option) => option.value))}>
                    {indexedDocuments.map((doc) => (
                      <option key={doc.id} value={doc.id}>{doc.title || doc.original_filename}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>{t.categoryLabel}</span>
                  <input value={selectedCategory} onChange={(event) => setSelectedCategory(event.target.value)} placeholder={t.placeholders.filter} />
                </label>
                <label>
                  <span>{t.tagsLabel}</span>
                  <input value={selectedTags} onChange={(event) => setSelectedTags(event.target.value)} placeholder={t.placeholders.tags} />
                </label>
                <label>
                  <span>{t.formatLabel}</span>
                  <select value={answerFormat} onChange={(event) => setAnswerFormat(event.target.value)}>
                    {ANSWER_FORMATS.map((option) => (
                      <option key={option.value} value={option.value}>{option[language]}</option>
                    ))}
                  </select>
                </label>
              </div>
              <label>
                <span>{t.questionLabel}</span>
                <textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={t.askHint} />
              </label>
              <div className="action-row">
                <button className="primary" onClick={handleAsk} disabled={loading || !question.trim()}>
                  {loading ? "..." : t.askButton}
                </button>
                <button className="secondary" disabled>{t.exportButton}</button>
                <button className="secondary" disabled>{t.shareButton}</button>
              </div>
            </div>
          )}

          {activeTab === "compare" && (
            <div className="workflow-form">
              <div className="field-grid">
                <label>
                  <span>{t.compareLeft}</span>
                  <select value={leftDocumentId} onChange={(event) => setLeftDocumentId(event.target.value)}>
                    <option value=""></option>
                    {indexedDocuments.map((doc) => (
                      <option key={doc.id} value={doc.id}>{doc.title || doc.original_filename}</option>
                    ))}
                  </select>
                </label>
                <label>
                  <span>{t.compareRight}</span>
                  <select value={rightDocumentId} onChange={(event) => setRightDocumentId(event.target.value)}>
                    <option value=""></option>
                    {indexedDocuments.map((doc) => (
                      <option key={doc.id} value={doc.id}>{doc.title || doc.original_filename}</option>
                    ))}
                  </select>
                </label>
              </div>
              <label>
                <span>{t.questionLabel}</span>
                <textarea value={compareQuestion} onChange={(event) => setCompareQuestion(event.target.value)} placeholder={t.placeholders.compare} />
              </label>
              <div className="action-row">
                <button className="primary" onClick={handleCompare} disabled={loading || !leftDocumentId || !rightDocumentId || !compareQuestion.trim()}>
                  {loading ? "..." : t.compareButton}
                </button>
              </div>
            </div>
          )}

          {activeTab === "synthesize" && (
            <div className="workflow-form">
              <label>
                <span>{t.synthDocs}</span>
                <select multiple value={synthesisDocumentIds} onChange={(event) => setSynthesisDocumentIds(Array.from(event.target.selectedOptions).map((option) => option.value))}>
                  {indexedDocuments.map((doc) => (
                    <option key={doc.id} value={doc.id}>{doc.title || doc.original_filename}</option>
                  ))}
                </select>
              </label>
              <label>
                <span>{t.questionLabel}</span>
                <textarea value={synthesisQuestion} onChange={(event) => setSynthesisQuestion(event.target.value)} placeholder={t.placeholders.synth} />
              </label>
              <div className="action-row">
                <button className="primary" onClick={handleSynthesis} disabled={loading || synthesisDocumentIds.length < 2 || !synthesisQuestion.trim()}>
                  {loading ? "..." : t.synthButton}
                </button>
              </div>
            </div>
          )}
        </section>

        <section className="library-grid">
          <div className="library-card" id="documents">
            <div className="section-head">
              <div>
                <span className="eyebrow muted">{t.docLibrary}</span>
                <h3>{t.docLibrary}</h3>
              </div>
              <label className="toggle-check">
                <input type="checkbox" checked={latestOnly} onChange={(event) => setLatestOnly(event.target.checked)} />
                <span>{t.latestOnly}</span>
              </label>
            </div>

            <form className="upload-form" onSubmit={handleUpload}>
              <div className="upload-title">
                <strong>{t.upload}</strong>
                <small>{t.uploadHint}</small>
              </div>
              <input type="file" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} />
              <div className="field-grid">
                <label>
                  <span>{t.titleLabel}</span>
                  <input value={uploadTitle} onChange={(event) => setUploadTitle(event.target.value)} placeholder={t.placeholders.title} />
                </label>
                <label>
                  <span>{t.categoryLabel}</span>
                  <input value={uploadCategory} onChange={(event) => setUploadCategory(event.target.value)} placeholder={t.placeholders.category} />
                </label>
                <label>
                  <span>{t.versionLabel}</span>
                  <input value={uploadVersion} onChange={(event) => setUploadVersion(event.target.value)} placeholder={t.placeholders.version} />
                </label>
                <label>
                  <span>{t.tagsLabel}</span>
                  <input value={uploadTags} onChange={(event) => setUploadTags(event.target.value)} placeholder={t.placeholders.tags} />
                </label>
              </div>
              <label>
                <span>Date</span>
                <input type="date" value={uploadDate} onChange={(event) => setUploadDate(event.target.value)} />
              </label>
              <button className="secondary" disabled={!selectedFile || uploading}>
                {uploading ? "..." : t.upload}
              </button>
            </form>

            <div className="filter-row">
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={t.placeholders.search} />
              <input value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)} placeholder={t.placeholders.filter} />
            </div>

            <div className="document-list">
              {displayedDocuments.length === 0 && <div className="empty-box">{t.documentsEmpty}</div>}
              {displayedDocuments.map((doc) => (
                <article key={doc.id} id={`doc-${doc.original_filename}`} className={`document-row ${uniqueDocs.includes(doc.original_filename) ? "linked" : ""}`}>
                  <div>
                    <strong>{doc.title || doc.original_filename}</strong>
                    <p>{doc.original_filename}</p>
                    <small>
                      {[doc.category || "-", doc.version || `v${doc.version_number}`, doc.tags.join(", "), doc.is_latest_version ? "latest" : "superseded"]
                        .filter(Boolean)
                        .join(" · ")}
                    </small>
                  </div>
                  <div className="row-actions">
                    <button className="ghost" onClick={() => handleSummary(doc.id, doc.title || doc.original_filename)}>{t.summaryButton}</button>
                    <button className="ghost danger" onClick={() => handleDelete(doc.id)}>{t.deleteButton}</button>
                  </div>
                </article>
              ))}
            </div>
          </div>

          <div className="library-card" id="historique">
            <div className="section-head">
              <div>
                <span className="eyebrow muted">{t.reviewHistory}</span>
                <h3>{t.reviewHistory}</h3>
              </div>
            </div>
            {history.length === 0 && <div className="empty-box">{t.historyEmpty}</div>}
            <div className="history-list">
              {history.map((item) => (
                <article key={item.id} className="history-row">
                  <strong>{item.question}</strong>
                  <p>{item.answer}</p>
                  <small>
                    {new Date(item.created_at).toLocaleString(language === "fr" ? "fr-FR" : "en-US")} · {item.sources_json.length} source(s)
                  </small>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>

      <aside className="right-rail">
        <section className="evidence-card">
          <div className="section-head">
            <div>
              <span className="eyebrow muted">{t.evidence}</span>
              <h3>{t.resultTitle}</h3>
            </div>
            {result && <span className={`safety-badge ${safetyClass(result.safety)}`}>{mapSafety(result.safety, t)}</span>}
          </div>

          {!result && <div className="empty-box">{t.sourcePanelEmpty}</div>}

          {result && (
            <>
              <div className="answer-box">
                <p>{stripSourcesLine(result.answer || t.noReliableAnswer)}</p>
              </div>

              <div className="trust-grid">
                <TrustMetric label={t.confidenceLine} value={`${mapConfidence(result.confidence || result.confidence_label, t)}${confidenceSuffix(result, language)}`} />
                <TrustMetric label={t.safetyLine} value={mapSafety(result.safety, t)} />
                <TrustMetric label={t.coverage} value={result.evidence_summary || `${result.sources?.length || 0} source(s)`} />
              </div>

              <div className="why-box">
                <h4>{t.why}</h4>
                <ul className="plain-list">
                  <li>{t.selectedDocs}: {uniqueDocs.join(", ") || "-"}</li>
                  <li>{t.selectedBecause}: {result.confidence_reason || t.explanationLine}</li>
                  <li>{t.coverage}: {result.used_context_count || 0} source(s)</li>
                </ul>
              </div>

              {result.clarification_needed && (
                <div className="clarify-box">
                  <strong>{result.clarifying_question}</strong>
                  <p>{t.filtersHint}</p>
                </div>
              )}

              {result.sections?.length > 0 && (
                <div className="section-list">
                  {result.sections.map((section) => (
                    <article key={section.title} className="mini-section">
                      <strong>{section.title}</strong>
                      {section.content && <p>{section.content}</p>}
                      {section.items?.length > 0 && (
                        <ul className="plain-list compact">
                          {section.items.map((item, index) => <li key={`${section.title}-${index}`}>{item}</li>)}
                        </ul>
                      )}
                    </article>
                  ))}
                </div>
              )}

              <div className="evidence-list">
                {(result.sources || []).map((source) => (
                  <article
                    key={source.chunk_id}
                    className={`evidence-row ${activeSourceId === source.chunk_id ? "active" : ""}`}
                    onMouseEnter={() => setActiveSourceId(source.chunk_id)}
                    onMouseLeave={() => setActiveSourceId(null)}
                    onClick={() => scrollToDocument(source.document_name)}
                  >
                    <div className="evidence-head">
                      <strong>{source.document_name}</strong>
                      <span>{typeof source.score === "number" ? source.score.toFixed(2) : "-"}</span>
                    </div>
                    <p>{highlightTerms(source.excerpt, question)}</p>
                  </article>
                ))}
              </div>

              <div className="follow-up-box">
                <h4>{t.suggestions}</h4>
                <div className="pill-row">
                  {[...(result.suggestions || []), ...FOLLOW_UPS[language]].slice(0, 5).map((item) => (
                    <button
                      key={item}
                      className="soft-pill interactive"
                      onClick={() => {
                        setQuestion(item);
                        setActiveTab("ask");
                      }}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}
        </section>
      </aside>
    </div>
  );
}

function Metric({ value, label }) {
  return (
    <div className="metric-v3">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function InfoSection({ title, items, rich = false }) {
  return (
    <section className="info-card">
      <div className="section-head">
        <div>
          <span className="eyebrow muted">{title}</span>
          <h3>{title}</h3>
        </div>
      </div>
      <div className={rich ? "info-grid" : "impact-list"}>
        {items.map(([label, text]) => (
          <article key={label} className="info-item">
            <strong>{label}</strong>
            {text && <p>{text}</p>}
          </article>
        ))}
      </div>
    </section>
  );
}

function TrustMetric({ label, value }) {
  return (
    <div className="trust-metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function mapConfidence(value, t) {
  const normalized = String(value || "").toLowerCase();
  if (normalized.includes("high") || normalized.includes("élev")) return t.status.high;
  if (normalized.includes("medium") || normalized.includes("moy")) return t.status.medium;
  return t.status.low;
}

function confidenceSuffix(result, language) {
  const count = result.sources?.length || 0;
  if (!count) return "";
  return language === "fr" ? ` (${count} sources cohérentes)` : ` (${count} consistent sources)`;
}

function mapSafety(value, t) {
  if (value === "Grounded") return t.status.grounded;
  if (value === "Limited") return t.status.limited;
  return t.status.none;
}

function safetyClass(value) {
  if (value === "Grounded") return "grounded";
  if (value === "Limited") return "limited";
  return "none";
}

function stripSourcesLine(text = "") {
  return text.replace(/\n\s*Sources:\s.*$/s, "").trim();
}

function slugify(value) {
  return value.toLowerCase().replace(/[^a-zA-Z0-9]+/g, "-");
}

function highlightTerms(text, query) {
  const terms = [...new Set((query || "").toLowerCase().match(/[a-zA-ZÀ-ÿ]{4,}/g) || [])].slice(0, 6);
  let output = text;
  terms.forEach((term) => {
    output = output.replace(new RegExp(`(${escapeRegExp(term)})`, "gi"), "<mark>$1</mark>");
  });
  return <span dangerouslySetInnerHTML={{ __html: output }} />;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export default App;
