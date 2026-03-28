import { useEffect, useState } from "react";
import { api } from "./api";

const COPY = {
  fr: {
    appName: "Knowledge Copilot Builder",
    shellLabel: "Construire un assistant fondé",
    heroBadge: "AI knowledge product",
    heroTitle: "Construisez un assistant IA fondé sur vos documents",
    heroSubtitle: "Configurez le comportement, cadrez le corpus et montrez des réponses avec preuves visibles.",
    heroDescription:
      "Un produit IA crédible montre son retrieval, son périmètre, son état runtime et la logique qui mène à la réponse.",
    heroAudience: "Pour équipes internes, démos clients et portfolio AI engineer / AI builder.",
    proofOneTitle: "Réponses fondées",
    proofOneBody: "Chaque réponse reste ancrée dans des extraits visibles.",
    proofTwoTitle: "Contrôles builder",
    proofTwoBody: "Profils d’assistant, scope retrieval, ton, format et publication dans une même surface.",
    proofThreeTitle: "Signaux de prod",
    proofThreeBody: "Runtime, retrieval mode, historique et confiance restent visibles.",
    builderCanvas: "Studio builder",
    liveSystem: "Système actif",
    publishedAssistants: "Assistants publiés",
    indexedDocs: "Documents indexés",
    draftMode: "Draft en cours",
    draftModeHint: "Créez un assistant, sauvegardez-le, testez-le.",
    builderStatus: "Statut builder",
    runtimeMode: "Runtime",
    retrievalMode: "Retrieval",
    llmMode: "LLM",
    scopeSummary: "Périmètre",
    scopeAll: "Corpus complet",
    docsScoped: "docs ciblés",
    tagsScoped: "tags",
    categoriesScoped: "catégories",
    builderWorkflowTitle: "Builder workflow",
    builderWorkflowSubtitle: "On voit comment l’assistant est configuré, testé et prêt à être publié.",
    engineerSignalsTitle: "Signaux AI engineer",
    engineerSignalsSubtitle: "Runtime, retrieval et validation restent lisibles dans l’interface.",
    configureTitle: "Configurer",
    configureBody: "Définissez le rôle, le ton, les instructions système et le format de réponse.",
    scopeTitle: "Cadrer le corpus",
    scopeBody: "Limitez par documents, tags, catégories et dernières versions pour contrôler le retrieval.",
    evaluateTitle: "Tester en live",
    evaluateBody: "Interrogez le corpus avec preuves, scores, historique et comportement assistant observables.",
    publishTitle: "Publier",
    publishBody: "Passez de draft à published avec un assistant par défaut prêt à servir de façade produit.",
    runtimeSignalTitle: "Runtime observable",
    evalSignalTitle: "Boucle de validation",
    shippingSignalTitle: "Statut de shipping",
    runtimeSignalDetail: "Healthcheck, modes d’exécution et retrieval visibles sans cacher les compromis.",
    evalSignalDetail: "Historique, sources et confiance rendent chaque test lisible pour recruteur, reviewer ou client.",
    shippingSignalDetail: "Le produit distingue draft, default et published comme un vrai builder.",
    traceCount: "traces",
    stackLabel: "Stack",
    publishedState: "Published",
    draftState: "Draft",
    narrativeTitle: "Pourquoi ça tient",
    narrativeOneTitle: "Valeur produit",
    narrativeOneBody: "Le produit répond à un usage concret: interroger un corpus interne avec confiance et traçabilité.",
    narrativeTwoTitle: "Crédibilité technique",
    narrativeTwoBody: "La chaîne retrieval -> ranking -> answer -> evidence reste visible et vérifiable.",
    narrativeThreeTitle: "Lecture recruteur / client",
    narrativeThreeBody: "On ne voit plus un chatbot, mais une base produit configurable prête à être industrialisée.",
    askButton: "Analyser",
    askLabel: "Votre question",
    askPlaceholder: "Ex: Quelle est la politique de télétravail ?",
    advancedFilters: "Filtres avancés",
    advancedFiltersShow: "Afficher les filtres avancés",
    advancedFiltersHide: "Masquer les filtres avancés",
    formatLabel: "Format",
    scopeLabel: "Limiter à certains documents",
    categoryLabel: "Catégorie",
    tagsLabel: "Tags",
    resultTitle: "Réponse",
    evidenceTitle: "Couche de confiance",
    confidence: "Confiance",
    safety: "Sécurité",
    sources: "Sources",
    why: "Pourquoi cette réponse",
    sourcePanelEmpty:
      "Après votre question, ce panneau affichera le niveau de confiance, les sources retenues et l'explication.",
    emptyPromptTitle: "La confiance s'affichera ici",
    emptyPromptBody:
      "Commencez par poser une question. La réponse apparaîtra au centre, avec les preuves détaillées dans le panneau latéral.",
    noReliableAnswer: "Je ne sais pas sur la base des documents disponibles.",
    confidenceLine: "Confiance",
    safetyLine: "Sécurité",
    explanationLine: "Les extraits retenus couvrent le sujet demandé et justifient la réponse affichée.",
    loading: "Analyse en cours...",
    runtimeConnected: "Connecté",
    runtimeUnavailable: "Indisponible",
    language: "Langue",
    darkMode: "Mode sombre",
    builderTitle: "AI Builder",
    builderHint: "Configurez rôle, corpus, réglages et état de publication.",
    activeAssistant: "Assistant actif",
    newAssistant: "Nouveau draft",
    saveAssistant: "Enregistrer l’assistant",
    assistantName: "Nom de l’assistant",
    assistantDescription: "Positionnement",
    assistantInstructions: "Instructions",
    assistantTone: "Ton",
    topKLabel: "Top K",
    rerankLabel: "Reranking",
    rerankOff: "Sans reranking",
    publishedLabel: "Publié",
    defaultLabel: "Par défaut",
    builderSaved: "Assistant enregistré.",
    noAssistant: "Aucun assistant",
    settingsTitle: "Réglages",
    libraryTitle: "Bibliothèque",
    historyTitle: "Historique",
    uploadTitle: "Ajouter un document",
    uploadHint: "PDF, DOCX, TXT, MD, CSV",
    titleLabel: "Titre",
    versionLabel: "Version",
    placeholders: {
      title: "Ex. Politique RH 2026",
      category: "RH, Support, Opérations",
      version: "v2026.1",
      tags: "rh, onboarding, politique",
      search: "Rechercher un document",
      filter: "Filtrer par catégorie",
    },
    latestOnly: "Dernières versions seulement",
    summaryButton: "Résumer",
    deleteButton: "Supprimer",
    documentsEmpty: "Aucun document indexé pour le moment.",
    libraryEmptyHint: "Ajoutez un document ou rechargez vos données.",
    historyEmpty: "Aucune interaction enregistrée pour le moment.",
    historyEmptyHint: "Les dernières réponses apparaîtront ici.",
    examplesTitle: "Exemples",
    examples: [
      "Compare les procédures d’incident",
      "Résume le handbook RH",
      "Quelles sont les règles de remboursement ?",
    ],
    continueTitle: "Continuer",
    suggestedQuestions: "Suggestions de suivi",
    selectedDocs: "Documents retenus",
    coverage: "Couverture",
    status: {
      grounded: "Fondée",
      limited: "Limitée",
      none: "Aucune réponse fiable",
      high: "Élevée",
      medium: "Moyenne",
      low: "Faible",
    },
    answerMeta: {
      answer: "Réponse",
      confidence: "Confiance",
      safety: "Sécurité",
      why: "Pourquoi cette réponse",
      sources: "Sources",
    },
    open: "Ouvrir",
    close: "Fermer",
    sourcePreview: "Extrait source",
    document: "Document",
    relevance: "Pertinence",
    location: "Localisation",
    metadata: "Métadonnées",
    askCtaHint: "Réponse, périmètre, preuves et logique de confiance au même endroit.",
    openSourceHint: "Cliquer pour ouvrir l'extrait",
  },
  en: {
    appName: "Knowledge Copilot Builder",
    shellLabel: "Build a grounded assistant",
    heroBadge: "AI knowledge product",
    heroTitle: "Build an AI assistant grounded in your documents",
    heroSubtitle: "Configure behavior, scope the corpus, and show answers with visible evidence.",
    heroDescription:
      "A credible AI product exposes retrieval, scope, runtime state, and the logic behind each response.",
    heroAudience: "For internal teams, client demos, and AI engineer / AI builder portfolio work.",
    proofOneTitle: "Grounded answers",
    proofOneBody: "Answers stay anchored in visible excerpts.",
    proofTwoTitle: "Builder controls",
    proofTwoBody: "Assistant profiles, retrieval scope, tone, format, and publish state live in one surface.",
    proofThreeTitle: "Production signals",
    proofThreeBody: "Runtime, retrieval mode, history, and confidence stay exposed.",
    builderCanvas: "Builder studio",
    liveSystem: "Live system",
    publishedAssistants: "Published assistants",
    indexedDocs: "Indexed documents",
    draftMode: "Draft in progress",
    draftModeHint: "Create an assistant, save it, test it.",
    builderStatus: "Builder status",
    runtimeMode: "Runtime",
    retrievalMode: "Retrieval",
    llmMode: "LLM",
    scopeSummary: "Scope",
    scopeAll: "Full corpus",
    docsScoped: "scoped docs",
    tagsScoped: "tags",
    categoriesScoped: "categories",
    builderWorkflowTitle: "Builder workflow",
    builderWorkflowSubtitle: "You can see how the assistant is configured, tested, and ready to ship.",
    engineerSignalsTitle: "AI engineer signals",
    engineerSignalsSubtitle: "Runtime, retrieval, and validation stay legible in the interface.",
    configureTitle: "Configure",
    configureBody: "Define the role, tone, system instructions, and answer format.",
    scopeTitle: "Scope the corpus",
    scopeBody: "Restrict retrieval with documents, tags, categories, and latest-version controls.",
    evaluateTitle: "Test live",
    evaluateBody: "Query the corpus with visible evidence, scores, history, and assistant behavior.",
    publishTitle: "Publish",
    publishBody: "Move from draft to published with a default assistant ready to act as the product surface.",
    runtimeSignalTitle: "Observable runtime",
    evalSignalTitle: "Validation loop",
    shippingSignalTitle: "Shipping status",
    runtimeSignalDetail: "Healthcheck, runtime modes, and retrieval modes stay visible instead of hidden.",
    evalSignalDetail: "History, sources, and confidence make each test reviewable for clients, recruiters, and reviewers.",
    shippingSignalDetail: "The product distinguishes draft, default, and published states like a real builder.",
    traceCount: "traces",
    stackLabel: "Stack",
    publishedState: "Published",
    draftState: "Draft",
    narrativeTitle: "Why it holds up",
    narrativeOneTitle: "Product value",
    narrativeOneBody: "The product solves a clear use case: query internal knowledge with confidence and traceability.",
    narrativeTwoTitle: "Technical credibility",
    narrativeTwoBody: "The retrieval -> ranking -> answer -> evidence chain stays visible and reviewable.",
    narrativeThreeTitle: "Recruiter / client read",
    narrativeThreeBody: "It no longer reads like a chatbot demo, but like a configurable product surface.",
    askButton: "Analyze",
    askLabel: "Your question",
    askPlaceholder: "Ex: What is the remote work policy?",
    advancedFilters: "Advanced filters",
    advancedFiltersShow: "Show advanced filters",
    advancedFiltersHide: "Hide advanced filters",
    formatLabel: "Format",
    scopeLabel: "Limit to documents",
    categoryLabel: "Category",
    tagsLabel: "Tags",
    resultTitle: "Answer",
    evidenceTitle: "Trust layer",
    confidence: "Confidence",
    safety: "Safety",
    sources: "Sources",
    why: "Why this answer",
    sourcePanelEmpty:
      "After your question, this panel will show confidence, selected sources, and the answer rationale.",
    emptyPromptTitle: "Trust appears here",
    emptyPromptBody:
      "Start with a question. The answer will appear in the center, with detailed evidence in the side panel.",
    noReliableAnswer: "I don't know based on available documents.",
    confidenceLine: "Confidence",
    safetyLine: "Safety",
    explanationLine: "Selected excerpts cover the request and justify the displayed answer.",
    loading: "Analyzing...",
    runtimeConnected: "Connected",
    runtimeUnavailable: "Unavailable",
    language: "Language",
    darkMode: "Dark mode",
    builderTitle: "AI Builder",
    builderHint: "Configure role, corpus, controls, and publish state.",
    activeAssistant: "Active assistant",
    newAssistant: "New draft",
    saveAssistant: "Save assistant",
    assistantName: "Assistant name",
    assistantDescription: "Positioning",
    assistantInstructions: "Instructions",
    assistantTone: "Tone",
    topKLabel: "Top K",
    rerankLabel: "Reranking",
    rerankOff: "No reranking",
    publishedLabel: "Published",
    defaultLabel: "Default",
    builderSaved: "Assistant saved.",
    noAssistant: "No assistant",
    settingsTitle: "Settings",
    libraryTitle: "Library",
    historyTitle: "History",
    uploadTitle: "Upload document",
    uploadHint: "PDF, DOCX, TXT, MD, CSV",
    titleLabel: "Title",
    versionLabel: "Version",
    placeholders: {
      title: "Ex. HR Policy 2026",
      category: "HR, Support, Operations",
      version: "v2026.1",
      tags: "hr, onboarding, policy",
      search: "Search documents",
      filter: "Filter by category",
    },
    latestOnly: "Latest versions only",
    summaryButton: "Summarize",
    deleteButton: "Delete",
    documentsEmpty: "No indexed documents yet.",
    libraryEmptyHint: "Upload a document or refresh your data.",
    historyEmpty: "No recorded interactions yet.",
    historyEmptyHint: "Recent answers will appear here.",
    examplesTitle: "Examples",
    examples: [
      "Compare incident procedures",
      "Summarize the HR handbook",
      "What are the reimbursement rules?",
    ],
    continueTitle: "Continue",
    suggestedQuestions: "Follow-up suggestions",
    selectedDocs: "Selected documents",
    coverage: "Coverage",
    status: {
      grounded: "Grounded",
      limited: "Limited",
      none: "No reliable answer",
      high: "High",
      medium: "Medium",
      low: "Low",
    },
    answerMeta: {
      answer: "Answer",
      confidence: "Confidence",
      safety: "Safety",
      why: "Why this answer",
      sources: "Sources",
    },
    open: "Open",
    close: "Close",
    sourcePreview: "Source excerpt",
    document: "Document",
    relevance: "Relevance",
    location: "Location",
    metadata: "Metadata",
    askCtaHint: "Answer, scope, evidence, and confidence logic in one place.",
    openSourceHint: "Click to open excerpt",
  },
};

const ANSWER_FORMATS = [
  { value: "concise", fr: "Concise", en: "Concise" },
  { value: "detailed", fr: "Détaillée", en: "Detailed" },
  { value: "checklist", fr: "Checklist", en: "Checklist" },
  { value: "summary", fr: "Résumé", en: "Summary" },
];

const FOLLOW_UPS = {
  fr: [
    "Peux-tu préciser les exceptions importantes ?",
    "Quels extraits justifient cette réponse ?",
    "Résume les points à partager à l’équipe.",
  ],
  en: [
    "Can you clarify the important exceptions?",
    "Which excerpts support this answer?",
    "Summarize the points to share with the team.",
  ],
};

const TONE_OPTIONS = [
  { value: "balanced", fr: "Équilibré", en: "Balanced" },
  { value: "executive", fr: "Exécutif", en: "Executive" },
  { value: "support", fr: "Support", en: "Support" },
  { value: "compliance", fr: "Conformité", en: "Compliance" },
  { value: "friendly", fr: "Accessible", en: "Friendly" },
];

const EMPTY_ASSISTANT_FORM = {
  name: "",
  description: "",
  instructions: "",
  tone: "balanced",
  language: "auto",
  answer_format: "concise",
  tags: "",
  categories: "",
  latest_only: true,
  retrieval_top_k: 5,
  use_reranking: true,
  is_default: false,
  published: false,
  document_ids: [],
};

function App() {
  const [language, setLanguage] = useState("fr");
  const [darkMode, setDarkMode] = useState(true);
  const [health, setHealth] = useState(null);
  const [assistants, setAssistants] = useState([]);
  const [selectedAssistantId, setSelectedAssistantId] = useState(null);
  const [assistantForm, setAssistantForm] = useState(EMPTY_ASSISTANT_FORM);
  const [savingAssistant, setSavingAssistant] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [history, setHistory] = useState([]);
  const [result, setResult] = useState(null);
  const [activeSourceId, setActiveSourceId] = useState(null);
  const [previewSource, setPreviewSource] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answerFormat, setAnswerFormat] = useState("concise");
  const [selectedDocumentIds, setSelectedDocumentIds] = useState([]);
  const [selectedTags, setSelectedTags] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadCategory, setUploadCategory] = useState("");
  const [uploadVersion, setUploadVersion] = useState("");
  const [uploadTags, setUploadTags] = useState("");
  const [uploadDate, setUploadDate] = useState("");
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [latestOnly, setLatestOnly] = useState(true);
  const [conversationMemory, setConversationMemory] = useState([]);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [showLibrary, setShowLibrary] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const t = COPY[language];
  const activeAssistant = selectedAssistantId
    ? assistants.find((item) => item.id === selectedAssistantId) || null
    : null;
  const publishedAssistants = assistants.filter((item) => item.published).length;
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
  const previewDocument = previewSource
    ? documents.find((item) => item.original_filename === previewSource.document_name)
    : null;
  const builderScope = summarizeAssistantScope(activeAssistant, indexedDocuments.length, t);

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? "dark" : "light";
  }, [darkMode]);

  useEffect(() => {
    loadApp();
  }, [latestOnly]);

  useEffect(() => {
    if (!activeAssistant) {
      setAssistantForm(EMPTY_ASSISTANT_FORM);
      return;
    }
    const nextForm = assistantToForm(activeAssistant);
    setAssistantForm(nextForm);
    setAnswerFormat(activeAssistant.answer_format || "concise");
    setSelectedTags((activeAssistant.tags || []).join(", "));
    setSelectedCategory(activeAssistant.categories?.[0] || "");
    setSelectedDocumentIds(activeAssistant.document_ids || []);
  }, [activeAssistant?.id]);

  useEffect(() => {
    if (result?.sources?.length) {
      setActiveSourceId(result.sources[0].chunk_id);
    }
  }, [result]);

  async function loadApp() {
    try {
      const [healthData, assistantsData, docs, historyData] = await Promise.all([
        api.health(),
        api.assistants(),
        api.documents({ include_superseded: !latestOnly }),
        api.history(),
      ]);
      setHealth(healthData);
      setAssistants(assistantsData);
      setSelectedAssistantId((current) => {
        if (assistantsData.some((assistant) => assistant.id === current)) return current;
        return assistantsData.find((assistant) => assistant.is_default)?.id || assistantsData[0]?.id || null;
      });
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

  function updateAssistantField(field, value) {
    setAssistantForm((current) => ({ ...current, [field]: value }));
  }

  async function handleAsk(nextQuestion = question) {
    if (!nextQuestion.trim()) return;
    try {
      setLoading(true);
      const payload = await api.query({
        question: nextQuestion,
        assistant_id: activeAssistant?.id || null,
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
      setQuestion(nextQuestion);
      setResult({ ...payload, mode: "ask", question: nextQuestion });
      rememberInteraction(nextQuestion, payload);
      setNotice(language === "fr" ? "Réponse générée avec preuves visibles." : "Answer generated with visible evidence.");
      await loadApp();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleNewAssistant() {
    setSelectedAssistantId(null);
    setAssistantForm(EMPTY_ASSISTANT_FORM);
  }

  async function handleSaveAssistant() {
    if (!assistantForm.name.trim()) {
      setError(language === "fr" ? "Donnez un nom à l’assistant." : "Give the assistant a name.");
      return;
    }
    try {
      setSavingAssistant(true);
      const payload = {
        name: assistantForm.name.trim(),
        description: assistantForm.description.trim(),
        instructions: assistantForm.instructions.trim(),
        tone: assistantForm.tone,
        language: assistantForm.language,
        answer_format: assistantForm.answer_format,
        tags: normalizeTags(assistantForm.tags),
        categories: normalizeTags(assistantForm.categories),
        latest_only: assistantForm.latest_only,
        retrieval_top_k: Number(assistantForm.retrieval_top_k) || 5,
        use_reranking: assistantForm.use_reranking,
        is_default: assistantForm.is_default,
        published: assistantForm.published,
        document_ids: assistantForm.document_ids,
      };
      const savedAssistant = selectedAssistantId
        ? await api.updateAssistant(selectedAssistantId, payload)
        : await api.createAssistant(payload);
      setNotice(t.builderSaved);
      await loadApp();
      setSelectedAssistantId(savedAssistant.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingAssistant(false);
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
        confidence_reason:
          language === "fr" ? "Résumé mono-document avec preuves sélectionnées." : "Single-document summary with selected evidence.",
        safety: "Grounded",
        suggestions:
          language === "fr"
            ? ["Compare avec une autre version.", "Transforme ce résumé en checklist."]
            : ["Compare with another version.", "Turn this summary into a checklist."],
        used_context_count: payload.sources?.length || 0,
        latency_ms: payload.latency_ms,
        status: "answered",
        mode: "summary",
        detected_language: language,
        question: label,
      });
      setPreviewSource(null);
      setNotice(language === "fr" ? `Résumé généré pour ${label}.` : `Summary generated for ${label}.`);
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

  function openSourcePreview(source) {
    setPreviewSource(source);
    setActiveSourceId(source.chunk_id);
    window.requestAnimationFrame(() => {
      document.getElementById("source-preview")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-head">
          <div className="brand-mark">AI</div>
          <div>
            <div className="brand-name">{t.appName}</div>
            <small>{health ? t.runtimeConnected : t.runtimeUnavailable}</small>
          </div>
        </div>

        <div className="sidebar-card">
          <div className="sidebar-section-title">{t.settingsTitle}</div>
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
        </div>

        <div className="sidebar-card">
          <div className="sidebar-section-title">{t.builderTitle}</div>
          <small>{t.builderHint}</small>
          <div className="builder-summary-card">
            <div className="builder-summary-head">
              <div>
                <strong>{activeAssistant?.name || t.draftMode}</strong>
                <small>{activeAssistant?.description || t.draftModeHint}</small>
              </div>
              <span className={`status-badge ${activeAssistant?.published ? "grounded" : "limited"}`}>
                {activeAssistant?.published ? t.publishedLabel : t.builderStatus}
              </span>
            </div>
            <div className="builder-chip-row">
              <span className="builder-chip">{builderScope}</span>
              <span className="builder-chip">{`${t.topKLabel} ${assistantForm.retrieval_top_k}`}</span>
              <span className="builder-chip">{assistantForm.use_reranking ? t.rerankLabel : t.rerankOff}</span>
            </div>
          </div>
          <label>
            <span>{t.activeAssistant}</span>
            <select
              value={selectedAssistantId || ""}
              onChange={(event) => setSelectedAssistantId(event.target.value || null)}
            >
              <option value="">{t.noAssistant}</option>
              {assistants.map((assistant) => (
                <option key={assistant.id} value={assistant.id}>
                  {assistant.name}
                </option>
              ))}
            </select>
          </label>
          <button className="ghost" onClick={handleNewAssistant}>
            {t.newAssistant}
          </button>
          <div className="upload-form compact-upload">
            <label>
              <span>{t.assistantName}</span>
              <input
                value={assistantForm.name}
                onChange={(event) => updateAssistantField("name", event.target.value)}
                placeholder={t.assistantName}
              />
            </label>
            <label>
              <span>{t.assistantDescription}</span>
              <input
                value={assistantForm.description}
                onChange={(event) => updateAssistantField("description", event.target.value)}
                placeholder={t.builderHint}
              />
            </label>
            <label>
              <span>{t.assistantInstructions}</span>
              <textarea
                value={assistantForm.instructions}
                onChange={(event) => updateAssistantField("instructions", event.target.value)}
                placeholder={t.builderHint}
              />
            </label>
            <div className="field-grid">
              <label>
                <span>{t.assistantTone}</span>
                <select
                  value={assistantForm.tone}
                  onChange={(event) => updateAssistantField("tone", event.target.value)}
                >
                  {TONE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option[language]}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>{t.language}</span>
                <select
                  value={assistantForm.language}
                  onChange={(event) => updateAssistantField("language", event.target.value)}
                >
                  <option value="auto">Auto</option>
                  <option value="fr">FR</option>
                  <option value="en">EN</option>
                </select>
              </label>
              <label>
                <span>{t.formatLabel}</span>
                <select
                  value={assistantForm.answer_format}
                  onChange={(event) => updateAssistantField("answer_format", event.target.value)}
                >
                  {ANSWER_FORMATS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option[language]}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>{t.topKLabel}</span>
                <input
                  type="number"
                  min="1"
                  max="12"
                  value={assistantForm.retrieval_top_k}
                  onChange={(event) => updateAssistantField("retrieval_top_k", event.target.value)}
                />
              </label>
              <label>
                <span>{t.tagsLabel}</span>
                <input
                  value={assistantForm.tags}
                  onChange={(event) => updateAssistantField("tags", event.target.value)}
                  placeholder={t.placeholders.tags}
                />
              </label>
              <label>
                <span>{t.categoryLabel}</span>
                <input
                  value={assistantForm.categories}
                  onChange={(event) => updateAssistantField("categories", event.target.value)}
                  placeholder={t.placeholders.category}
                />
              </label>
              <label>
                <span>{t.scopeLabel}</span>
                <select
                  multiple
                  value={assistantForm.document_ids}
                  onChange={(event) =>
                    updateAssistantField(
                      "document_ids",
                      Array.from(event.target.selectedOptions).map((option) => option.value),
                    )
                  }
                >
                  {indexedDocuments.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.title || doc.original_filename}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <label className="toggle-check">
              <input
                type="checkbox"
                checked={assistantForm.latest_only}
                onChange={(event) => updateAssistantField("latest_only", event.target.checked)}
              />
              <span>{t.latestOnly}</span>
            </label>
            <label className="toggle-check">
              <input
                type="checkbox"
                checked={assistantForm.use_reranking}
                onChange={(event) => updateAssistantField("use_reranking", event.target.checked)}
              />
              <span>{t.rerankLabel}</span>
            </label>
            <label className="toggle-check">
              <input
                type="checkbox"
                checked={assistantForm.published}
                onChange={(event) => updateAssistantField("published", event.target.checked)}
              />
              <span>{t.publishedLabel}</span>
            </label>
            <label className="toggle-check">
              <input
                type="checkbox"
                checked={assistantForm.is_default}
                onChange={(event) => updateAssistantField("is_default", event.target.checked)}
              />
              <span>{t.defaultLabel}</span>
            </label>
            <button className="primary" onClick={handleSaveAssistant} disabled={savingAssistant}>
              {savingAssistant ? "..." : t.saveAssistant}
            </button>
          </div>
        </div>

        <div className="sidebar-card minimal-card">
          <button className="sidebar-toggle" onClick={() => setShowLibrary((current) => !current)}>
            <span>{t.libraryTitle}</span>
            <strong>{showLibrary ? "−" : "+"}</strong>
          </button>
          {showLibrary && (
            <div className="sidebar-panel">
              <form className="upload-form compact-upload" onSubmit={handleUpload}>
                <div className="upload-title">
                  <strong>{t.uploadTitle}</strong>
                  <small>{t.uploadHint}</small>
                </div>
                <input type="file" onChange={(event) => setSelectedFile(event.target.files?.[0] || null)} />
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
                <label>
                  <span>Date</span>
                  <input type="date" value={uploadDate} onChange={(event) => setUploadDate(event.target.value)} />
                </label>
                <button className="secondary" disabled={!selectedFile || uploading}>
                  {uploading ? "..." : t.uploadTitle}
                </button>
              </form>

              <div className="filter-stack">
                <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={t.placeholders.search} />
                <input value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)} placeholder={t.placeholders.filter} />
                <label className="toggle-check">
                  <input type="checkbox" checked={latestOnly} onChange={(event) => setLatestOnly(event.target.checked)} />
                  <span>{t.latestOnly}</span>
                </label>
              </div>

              <div className="document-list">
                {displayedDocuments.length === 0 && (
                  <div className="empty-box polished-empty">
                    <strong>{t.documentsEmpty}</strong>
                    <p>{t.libraryEmptyHint}</p>
                  </div>
                )}
                {displayedDocuments.map((doc) => (
                  <article key={doc.id} className={`document-row ${uniqueDocs.includes(doc.original_filename) ? "linked" : ""}`}>
                    <div className="document-main">
                      <strong>{doc.title || doc.original_filename}</strong>
                      <small>
                        {[doc.category || "-", doc.version || `v${doc.version_number}`, doc.is_latest_version ? "latest" : "superseded"]
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
          )}
        </div>

        <div className="sidebar-card minimal-card">
          <button className="sidebar-toggle" onClick={() => setShowHistory((current) => !current)}>
            <span>{t.historyTitle}</span>
            <strong>{showHistory ? "−" : "+"}</strong>
          </button>
          {showHistory && (
            <div className="sidebar-panel history-panel">
              {history.length === 0 && (
                <div className="empty-box polished-empty">
                  <strong>{t.historyEmpty}</strong>
                  <p>{t.historyEmptyHint}</p>
                </div>
              )}
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
          )}
        </div>
      </aside>

      <main className="main-stage">
        {error && <div className="banner error">{error}</div>}
        {notice && <div className="banner success">{notice}</div>}

        <section className="hero-panel">
          <div className="hero-topline">
            <span className="eyebrow">{t.heroBadge}</span>
            <div className="answer-badges">
              {activeAssistant && <span className="status-badge neutral">{activeAssistant.name}</span>}
              <span className="status-pill">
                {health ? t.runtimeConnected : t.runtimeUnavailable}
              </span>
            </div>
          </div>
          <h1>{t.heroTitle}</h1>
          <p className="hero-subtitle">{t.heroSubtitle}</p>
          <p className="hero-description">{t.heroDescription}</p>
          <p className="hero-audience">{t.heroAudience}</p>
          <div className="proof-grid">
            <NarrativeCard title={t.proofOneTitle} body={t.proofOneBody} compact />
            <NarrativeCard title={t.proofTwoTitle} body={t.proofTwoBody} compact />
            <NarrativeCard title={t.proofThreeTitle} body={t.proofThreeBody} compact />
          </div>
          <div className="hero-metrics">
            <MetricCard
              label={t.builderCanvas}
              value={activeAssistant?.name || t.draftMode}
              detail={activeAssistant?.description || t.draftModeHint}
            />
            <MetricCard
              label={t.liveSystem}
              value={health ? t.runtimeConnected : t.runtimeUnavailable}
              detail={`${t.retrievalMode}: ${health?.retrieval_mode || "-"} · ${t.llmMode}: ${health?.llm_mode || "-"}`}
            />
            <MetricCard
              label={t.publishedAssistants}
              value={String(publishedAssistants)}
              detail={`${assistants.length} total`}
            />
            <MetricCard
              label={t.indexedDocs}
              value={String(indexedDocuments.length)}
              detail={builderScope}
            />
          </div>

          <div className="ask-panel">
            <label className="question-field">
              <span>{t.askLabel}</span>
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder={t.askPlaceholder}
              />
            </label>

            <div className="ask-actions">
              <button className="primary hero-cta" onClick={() => handleAsk()} disabled={loading || !question.trim()}>
                {loading ? t.loading : t.askButton}
              </button>
              <span className="cta-hint">{t.askCtaHint}</span>
            </div>

            <div className="examples-block">
              <div className="examples-head">
                <strong>{t.examplesTitle}</strong>
                <button className="ghost subtle-button" onClick={() => setShowAdvancedFilters((current) => !current)}>
                  {showAdvancedFilters ? t.advancedFiltersHide : t.advancedFiltersShow}
                </button>
              </div>
              <div className="examples-list">
                {t.examples.map((example) => (
                  <button
                    key={example}
                    className="example-chip"
                    onClick={() => {
                      setQuestion(example);
                    }}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>

            {showAdvancedFilters && (
              <div className="advanced-panel">
                <div className="advanced-head">
                  <strong>{t.advancedFilters}</strong>
                  <small>{t.shellLabel}</small>
                </div>
                <div className="field-grid">
                  <label>
                    <span>{t.formatLabel}</span>
                    <select value={answerFormat} onChange={(event) => setAnswerFormat(event.target.value)}>
                      {ANSWER_FORMATS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option[language]}
                        </option>
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
                    <span>{t.scopeLabel}</span>
                    <select multiple value={selectedDocumentIds} onChange={(event) => setSelectedDocumentIds(Array.from(event.target.selectedOptions).map((option) => option.value))}>
                      {indexedDocuments.map((doc) => (
                        <option key={doc.id} value={doc.id}>
                          {doc.title || doc.original_filename}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="narrative-stage">
          <div className="section-intro">
            <span className="eyebrow muted">{t.narrativeTitle}</span>
            <h2>{t.narrativeTitle}</h2>
          </div>
          <div className="narrative-grid">
            <NarrativeCard title={t.narrativeOneTitle} body={t.narrativeOneBody} />
            <NarrativeCard title={t.narrativeTwoTitle} body={t.narrativeTwoBody} />
            <NarrativeCard title={t.narrativeThreeTitle} body={t.narrativeThreeBody} />
          </div>
        </section>

        <section className="builder-stage">
          <div className="section-intro">
            <span className="eyebrow muted">{t.builderWorkflowTitle}</span>
            <h2>{t.engineerSignalsTitle}</h2>
            <p>{t.builderWorkflowSubtitle}</p>
          </div>

          <div className="workflow-grid">
            <WorkflowCard title={t.configureTitle} body={t.configureBody} step="01" />
            <WorkflowCard title={t.scopeTitle} body={`${t.scopeBody} ${builderScope}.`} step="02" />
            <WorkflowCard title={t.evaluateTitle} body={`${t.evaluateBody} ${history.length} ${t.traceCount}.`} step="03" />
            <WorkflowCard
              title={t.publishTitle}
              body={`${t.publishBody} ${activeAssistant?.published ? t.publishedState : t.draftState}.`}
              step="04"
            />
          </div>

          <div className="section-intro compact-intro">
            <span className="eyebrow muted">{t.engineerSignalsTitle}</span>
            <p>{t.engineerSignalsSubtitle}</p>
          </div>

          <div className="signal-grid">
            <SignalCard
              label={t.runtimeSignalTitle}
              value={`${health?.retrieval_mode || "-"} / ${health?.llm_mode || "-"}`}
              detail={t.runtimeSignalDetail}
            />
            <SignalCard
              label={t.evalSignalTitle}
              value={`${history.length} ${t.traceCount}`}
              detail={t.evalSignalDetail}
            />
            <SignalCard
              label={t.shippingSignalTitle}
              value={activeAssistant?.published ? t.publishedState : t.draftState}
              detail={t.shippingSignalDetail}
            />
          </div>

          <div className="stack-strip">
            <span className="stack-label">{t.stackLabel}</span>
            <div className="stack-chips">
              <span className="builder-chip">React</span>
              <span className="builder-chip">FastAPI</span>
              <span className="builder-chip">Qdrant</span>
              <span className="builder-chip">Grounded answers</span>
              <span className="builder-chip">Visible evidence</span>
              <span className="builder-chip">Assistant profiles</span>
            </div>
          </div>
        </section>

        {result && (
          <section className="answer-stage">
            <div className="answer-stage-head">
              <div>
                <span className="eyebrow muted">{t.resultTitle}</span>
                <h2>{result.question || question}</h2>
              </div>
              <div className="answer-badges">
                <span className={`status-badge ${safetyClass(result.safety)}`}>{mapSafety(result.safety, t)}</span>
                <span className="status-badge neutral">{mapConfidence(result.confidence || result.confidence_label, t)}</span>
              </div>
            </div>

            <article className="answer-card">
              <div className="answer-section">
                <span className="section-kicker">{t.answerMeta.answer}</span>
                <div className="formatted-answer">{renderRichAnswer(stripSourcesLine(result.answer || t.noReliableAnswer))}</div>
              </div>

              <div className="answer-summary-grid">
                <InfoTile
                  label={t.answerMeta.confidence}
                  value={`${mapConfidence(result.confidence || result.confidence_label, t)}${confidenceSuffix(result, language)}`}
                  tone={confidenceTone(result.confidence || result.confidence_label)}
                />
                <InfoTile label={t.answerMeta.safety} value={mapSafety(result.safety, t)} tone={safetyClass(result.safety)} />
                <InfoTile label={t.coverage} value={result.evidence_summary || `${result.sources?.length || 0} source(s)`} />
              </div>

              <div className="answer-section why-section">
                <span className="section-kicker">{t.answerMeta.why}</span>
                <p>{result.confidence_reason || t.explanationLine}</p>
              </div>

              {result.suggestions?.length > 0 || FOLLOW_UPS[language].length > 0 ? (
                <div className="answer-section">
                  <span className="section-kicker">{t.continueTitle}</span>
                  <div className="examples-list">
                    {[...(result.suggestions || []), ...FOLLOW_UPS[language]].slice(0, 5).map((item) => (
                      <button
                        key={item}
                        className="example-chip"
                        onClick={() => {
                          setQuestion(item);
                        }}
                      >
                        {item}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}
            </article>
          </section>
        )}

        {previewSource && (
          <section className="preview-card" id="source-preview">
            <div className="section-head">
              <div>
                <span className="eyebrow muted">{t.sourcePreview}</span>
                <h3>{previewSource.document_name}</h3>
              </div>
              <button className="ghost subtle-button" onClick={() => setPreviewSource(null)}>
                {t.close}
              </button>
            </div>
            <div className="preview-grid">
              <div className="preview-content">
                <div className="preview-excerpt">
                  <p>{highlightTerms(previewSource.excerpt, result?.question || question)}</p>
                </div>
              </div>
              <div className="preview-meta">
                <div className="preview-meta-card">
                  <strong>{t.document}</strong>
                  <span>{previewDocument?.title || previewSource.document_name}</span>
                </div>
                <div className="preview-meta-card">
                  <strong>{t.relevance}</strong>
                  <span>{typeof previewSource.score === "number" ? previewSource.score.toFixed(2) : "-"}</span>
                </div>
                <div className="preview-meta-card">
                  <strong>{t.location}</strong>
                  <span>
                    {previewSource.page_number
                      ? `${language === "fr" ? "Page" : "Page"} ${previewSource.page_number}`
                      : language === "fr"
                        ? "Contexte documentaire"
                        : "Document context"}
                  </span>
                </div>
                {previewDocument && (
                  <div className="preview-meta-card">
                    <strong>{t.metadata}</strong>
                    <span>
                      {[previewDocument.category, previewDocument.version || `v${previewDocument.version_number}`]
                        .filter(Boolean)
                        .join(" · ")}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}
      </main>

      <aside className="trust-rail">
        <section className="trust-card">
          <div className="section-head">
            <div>
              <span className="eyebrow muted">{t.evidenceTitle}</span>
              <h3>{t.evidenceTitle}</h3>
            </div>
          </div>

          {!result && (
            <div className="empty-box polished-empty trust-empty">
              <strong>{t.emptyPromptTitle}</strong>
              <p>{t.emptyPromptBody}</p>
              <small>{t.sourcePanelEmpty}</small>
            </div>
          )}

          {result && (
            <div className="trust-stack">
              <TrustSection title={t.confidence}>
                <TrustMetric
                  icon="confidence"
                  label={t.confidenceLine}
                  value={`${mapConfidence(result.confidence || result.confidence_label, t)}${confidenceSuffix(result, language)}`}
                  tone={confidenceTone(result.confidence || result.confidence_label)}
                />
              </TrustSection>

              <TrustSection title={t.safety}>
                <TrustMetric icon="safety" label={t.safetyLine} value={mapSafety(result.safety, t)} tone={safetyClass(result.safety)} />
              </TrustSection>

              <TrustSection title={t.sources}>
                <div className="evidence-list">
                  {(result.sources || []).map((source) => (
                    <article
                      key={source.chunk_id}
                      className={`evidence-row ${activeSourceId === source.chunk_id ? "active" : ""}`}
                      onMouseEnter={() => setActiveSourceId(source.chunk_id)}
                      onMouseLeave={() => setActiveSourceId(null)}
                      onClick={() => openSourcePreview(source)}
                    >
                      <div className="evidence-head">
                        <strong>{source.document_name}</strong>
                        <span>{typeof source.score === "number" ? source.score.toFixed(2) : "-"}</span>
                      </div>
                      <p>{highlightTerms(source.excerpt, result?.question || question)}</p>
                      <small className="source-hint">{t.openSourceHint}</small>
                    </article>
                  ))}
                </div>
              </TrustSection>

              <TrustSection title={t.why}>
                <div className="why-box">
                  <ul className="plain-list compact">
                    <li>{t.activeAssistant}: {result.assistant_name || activeAssistant?.name || "-"}</li>
                    <li>{t.selectedDocs}: {uniqueDocs.join(", ") || "-"}</li>
                    <li>{t.coverage}: {result.used_context_count || 0} source(s)</li>
                  </ul>
                  <p className="expanded-copy">{result.confidence_reason || t.explanationLine}</p>
                </div>
              </TrustSection>
            </div>
          )}
        </section>
      </aside>
    </div>
  );
}

function assistantToForm(assistant) {
  if (!assistant) return EMPTY_ASSISTANT_FORM;
  return {
    name: assistant.name || "",
    description: assistant.description || "",
    instructions: assistant.instructions || "",
    tone: assistant.tone || "balanced",
    language: assistant.language || "auto",
    answer_format: assistant.answer_format || "concise",
    tags: (assistant.tags || []).join(", "),
    categories: (assistant.categories || []).join(", "),
    latest_only: Boolean(assistant.latest_only),
    retrieval_top_k: assistant.retrieval_top_k || 5,
    use_reranking: Boolean(assistant.use_reranking),
    is_default: Boolean(assistant.is_default),
    published: Boolean(assistant.published),
    document_ids: assistant.document_ids || [],
  };
}

function summarizeAssistantScope(assistant, indexedDocumentCount, t) {
  if (!assistant) return t.scopeAll;
  const parts = [];
  if (assistant.document_ids?.length) parts.push(`${assistant.document_ids.length} ${t.docsScoped}`);
  if (assistant.tags?.length) parts.push(`${assistant.tags.length} ${t.tagsScoped}`);
  if (assistant.categories?.length) parts.push(`${assistant.categories.length} ${t.categoriesScoped}`);
  if (!parts.length) {
    return indexedDocumentCount ? `${t.scopeAll} · ${indexedDocumentCount}` : t.scopeAll;
  }
  return parts.join(" · ");
}

function MetricCard({ label, value, detail }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function WorkflowCard({ title, body, step }) {
  return (
    <article className="workflow-card">
      <span className="workflow-step">{step}</span>
      <strong>{title}</strong>
      <p>{body}</p>
    </article>
  );
}

function SignalCard({ label, value, detail }) {
  return (
    <article className="signal-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function NarrativeCard({ title, body, compact = false }) {
  return (
    <article className={`narrative-card${compact ? " compact" : ""}`}>
      <strong>{title}</strong>
      <p>{body}</p>
    </article>
  );
}

function InfoTile({ label, value, tone = "neutral" }) {
  return (
    <div className={`info-tile ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function TrustSection({ title, children }) {
  return (
    <section className="trust-section">
      <div className="trust-section-head">
        <SectionIcon type={sectionIconName(title)} />
        <h4>{title}</h4>
      </div>
      {children}
    </section>
  );
}

function TrustMetric({ label, value, tone = "neutral", icon }) {
  return (
    <div className={`trust-metric ${tone}`}>
      <div className="trust-metric-head">
        <div className="trust-metric-label">
          <MetricIcon type={icon} />
          <span>{label}</span>
        </div>
        <strong>{value}</strong>
      </div>
      <div className="trust-meter" aria-hidden="true">
        <div className={`trust-meter-bar ${tone}`} />
      </div>
    </div>
  );
}

function SectionIcon({ type }) {
  return (
    <span className={`section-icon ${type}`}>
      <MetricIcon type={type} />
    </span>
  );
}

function MetricIcon({ type }) {
  if (type === "confidence") {
    return (
      <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
        <path d="M3 11.5 6.2 8.3l2.2 2.2L13 6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  if (type === "safety") {
    return (
      <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
        <path d="M8 2.5 12.5 4v3.7c0 2.5-1.5 4.8-4.5 5.8-3-1-4.5-3.3-4.5-5.8V4L8 2.5Z" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
      <path d="M3 4.5h10M3 8h10M3 11.5h6.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function mapConfidence(value, t) {
  const normalized = String(value || "").toLowerCase();
  if (normalized.includes("high") || normalized.includes("élev")) return t.status.high;
  if (normalized.includes("medium") || normalized.includes("moy")) return t.status.medium;
  return t.status.low;
}

function confidenceTone(value) {
  const normalized = String(value || "").toLowerCase();
  if (normalized.includes("high") || normalized.includes("élev")) return "grounded";
  if (normalized.includes("medium") || normalized.includes("moy")) return "limited";
  return "none";
}

function confidenceSuffix(result, language) {
  const count = result.sources?.length || 0;
  if (!count) return "";
  return language === "fr" ? ` (${count} sources)` : ` (${count} sources)`;
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

function sectionIconName(title) {
  const normalized = String(title || "").toLowerCase();
  if (normalized.includes("conf")) return "confidence";
  if (normalized.includes("séc") || normalized.includes("saf")) return "safety";
  return "sources";
}

function stripSourcesLine(text = "") {
  return text.replace(/\n\s*Sources:\s.*$/s, "").trim();
}

function renderRichAnswer(text = "") {
  const lines = text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const blocks = [];
  let listItems = [];

  function flushList() {
    if (!listItems.length) return;
    blocks.push(
      <ul key={`list-${blocks.length}`} className="formatted-list">
        {listItems.map((item, index) => (
          <li key={`item-${index}`}>{formatInlineText(item)}</li>
        ))}
      </ul>,
    );
    listItems = [];
  }

  lines.forEach((line) => {
    if (/^[-*]\s+/.test(line)) {
      listItems.push(line.replace(/^[-*]\s+/, ""));
      return;
    }

    flushList();

    if (/^##\s+/.test(line)) {
      blocks.push(
        <h3 key={`h3-${blocks.length}`} className="formatted-heading">
          {formatInlineText(line.replace(/^##\s+/, ""))}
        </h3>,
      );
      return;
    }

    if (/^#\s+/.test(line)) {
      blocks.push(
        <h2 key={`h2-${blocks.length}`} className="formatted-heading large">
          {formatInlineText(line.replace(/^#\s+/, ""))}
        </h2>,
      );
      return;
    }

    blocks.push(
      <p key={`p-${blocks.length}`} className="formatted-paragraph">
        {formatInlineText(line)}
      </p>,
    );
  });

  flushList();
  return blocks;
}

function formatInlineText(text = "") {
  const tokens = text.split(/(\*\*.*?\*\*)/g).filter(Boolean);
  return tokens.map((token, index) => {
    if (token.startsWith("**") && token.endsWith("**")) {
      return <strong key={`strong-${index}`}>{token.slice(2, -2)}</strong>;
    }
    return token;
  });
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
