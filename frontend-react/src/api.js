const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8010";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const text = await response.text();
    let payload = null;
    try {
      payload = JSON.parse(text);
    } catch {}
    throw new Error(payload?.detail || text || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request("/health"),
  documents: (params = {}) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") searchParams.set(key, value);
    });
    const suffix = searchParams.toString() ? `?${searchParams.toString()}` : "";
    return request(`/documents${suffix}`);
  },
  history: () => request("/history"),
  feedback: (historyId, payload) =>
    request(`/history/${historyId}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  reindex: () => request("/reindex", { method: "POST" }),
  seedDemo: () => request("/demo/seed", { method: "POST" }),
  query: (payload) =>
    request("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  compare: (payload) =>
    request("/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  synthesize: (payload) =>
    request("/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  summarize: (documentId) =>
    request(`/documents/${documentId}/summary`, {
      method: "POST",
    }),
  upload: async ({ file, tags, title, category, documentDate, version }) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("tags", JSON.stringify(tags));
    if (title) formData.append("title", title);
    if (category) formData.append("category", category);
    if (documentDate) formData.append("document_date", documentDate);
    if (version) formData.append("version", version);
    return request("/upload", {
      method: "POST",
      body: formData,
    });
  },
  reimportDocument: async ({ documentId, file, tags, title, category, documentDate, version }) => {
    const formData = new FormData();
    formData.append("file", file);
    if (tags) formData.append("tags", JSON.stringify(tags));
    if (title) formData.append("title", title);
    if (category) formData.append("category", category);
    if (documentDate) formData.append("document_date", documentDate);
    if (version) formData.append("version", version);
    return request(`/documents/${documentId}/reimport`, {
      method: "POST",
      body: formData,
    });
  },
  deleteDocument: (documentId) =>
    request(`/documents/${documentId}`, {
      method: "DELETE",
    }),
};
