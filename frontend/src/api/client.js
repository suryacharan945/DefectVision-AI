/**
 * DefectVision AI — Centralized Production API Client
 * Connects directly to FastAPI backend running live inference on PatchCore + EfficientNet.
 */

const BASE_URL = import.meta.env.VITE_API_URL || ''; // Configurable for Vercel / Cloud deployments, falls back to relative proxy for dev

class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, options);
    
    if (!res.ok) {
      let errBody = {};
      try {
        errBody = await res.json();
      } catch (e) {
        errBody = { error: 'Unknown Error', detail: res.statusText };
      }
      throw new ApiError(
        errBody.error || errBody.detail || `HTTP ${res.status}`,
        res.status,
        errBody.detail || 'An unexpected error occurred during request.'
      );
    }
    
    return await res.json();
  } catch (err) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      'Network Connection Error',
      0,
      err.message || 'Unable to reach backend server at http://127.0.0.1:8000.'
    );
  }
}

export const api = {
  /**
   * Check backend health, active device, and category readiness
   */
  async checkHealth() {
    return request('/api/');
  },

  /**
   * Get curated test presets across all 15 categories for 1-click inspection
   */
  async getSamplePresets() {
    return request('/samples/presets');
  },

  /**
   * Run live PatchCore anomaly localization & EfficientNet classification
   * @param {File|Blob} file Image file to inspect
   * @param {string} category One of the 15 MVTec AD categories
   */
  async predict(file, category) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    return request('/predict', {
      method: 'POST',
      body: formData,
    });
  },

  /**
   * Generate operator-facing plain-English explanation
   */
  async explain({ category, defect_type, severity_level, severity_score, defect_area_pct, confidence_pct }) {
    return request('/explain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category,
        defect_type,
        severity_level,
        severity_score: parseFloat(severity_score),
        defect_area_pct: parseFloat(defect_area_pct),
        confidence_pct: parseFloat(confidence_pct),
      }),
    });
  },

  /**
   * Fetch 4-model benchmark comparison leaderboard
   */
  async getModelsComparison() {
    return request('/models/comparison');
  },

  /**
   * Fetch 15-category AUROC matrix across all 4 architectures
   */
  async getAurocMatrix() {
    return request('/reports/auroc-matrix');
  },

  /**
   * Fetch consolidated research summary report
   */
  async getResearchSummary() {
    return request('/reports/summary');
  },

  /**
   * Paginated severity log browser (1,725 benchmark items)
   */
  async getSeverityLogs({ category = '', severity_level = '', page = 1, page_size = 20 } = {}) {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (severity_level) params.append('severity_level', severity_level);
    params.append('page', page);
    params.append('page_size', page_size);

    return request(`/severity/logs?${params.toString()}`);
  },

  /**
   * Submit multi-image batch inspection
   */
  async submitBatch(files, category) {
    const formData = new FormData();
    for (const f of files) {
      formData.append('files', f);
    }
    formData.append('category', category);

    return request('/batch', {
      method: 'POST',
      body: formData,
    });
  },

  /**
   * Poll batch inspection status
   */
  async getBatchStatus(batchId) {
    return request(`/batch/${batchId}/status`);
  },

  /**
   * List past and completed batches
   */
  async getBatchList() {
    return request('/batch/list');
  },

  /**
   * Similarity search using image embedding against FAISS category gallery
   */
  async searchSimilarity(file, category) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    return request('/similarity', {
      method: 'POST',
      body: formData,
    });
  },

  /**
   * Get category representative FAISS gallery
   */
  async getCategoryGallery(category) {
    return request(`/similarity/category/${category}`);
  },

  /**
   * Get all 16 defect entries from knowledge base
   */
  async getRagEntries() {
    return request('/rag/entries');
  },

  /**
   * Ask RAG Defect Copilot
   */
  async askRAG(question) {
    return request('/rag/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
  },

  /**
   * Ask Conversational Analytics ("Ask the Data")
   */
  async askDashboard(question) {
    return request('/dashboard/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
  },

  /**
   * Fetch 3-stream production drift logs
   */
  async getDrift() {
    return request('/drift');
  },

  /**
   * Ask Root Cause Pattern Analysis
   */
  async askRCA(question) {
    return request('/rca/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
  },

  /**
   * Active Learning budget vs errors captured sensitivity curve
   */
  async getActiveLearningSensitivity() {
    return request('/active-learning/sensitivity');
  },

  /**
   * Run real-time in-memory frame inspection on camera snapshot
   * @param {Blob|File} frameBlob Binary JPEG blob from webcam or video element
   * @param {string} category One of the 15 MVTec AD categories
   */
  async inspectFrame(frameBlob, category = 'bottle') {
    const formData = new FormData();
    formData.append('frame', frameBlob, 'frame.jpg');
    formData.append('category', category);

    return request('/api/inspect-frame', {
      method: 'POST',
      body: formData,
    });
  },

  /**
   * Get direct MJPEG stream URL for live backend video feed
   * @param {string} category
   */
  getStreamUrl(category = 'bottle') {
    return `/stream/${encodeURIComponent(category)}`;
  },
};
