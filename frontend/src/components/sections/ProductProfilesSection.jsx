import React, { useState, useEffect } from 'react';
import {
  Boxes,
  PlusCircle,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  Archive,
  Trash2,
  Sliders,
  BarChart2,
  Play,
  Upload,
  Camera,
  Layers,
  Sparkles,
  Info,
  Shield,
  Clock,
  ArrowRight,
  X,
  FileCheck,
  AlertTriangle,
  Cpu
} from 'lucide-react';
import { api } from '../../api/client';

export default function ProductProfilesSection({ onSelectProfileForInspect }) {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');

  // Modals
  const [showWizard, setShowWizard] = useState(false);
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false);
  const [selectedAnalytics, setSelectedAnalytics] = useState(null);
  const [showEvaluateModal, setShowEvaluateModal] = useState(false);
  const [evaluateProfileId, setEvaluateProfileId] = useState(null);

  // Wizard state
  const [wizardStep, setWizardStep] = useState(1);
  const [productName, setProductName] = useState('');
  const [sku, setSku] = useState('');
  const [category, setCategory] = useState('bottle');
  const [camera, setCamera] = useState('CAM-EXT-01');
  const [station, setStation] = useState('Station 01 — Optical Quality');
  const [lighting, setLighting] = useState('ambient_or_diffuse');
  const [acquisition, setAcquisition] = useState('controlled_photography');
  const [calibrationRatio, setCalibrationRatio] = useState(0.30);
  const [coresetRatio, setCoresetRatio] = useState(0.10);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [filePreviews, setFilePreviews] = useState([]);
  const [wizardProgress, setWizardProgress] = useState('');
  const [wizardError, setWizardError] = useState(null);
  const [wizardResult, setWizardResult] = useState(null);

  // Evaluation state
  const [evalFiles, setEvalFiles] = useState([]);
  const [evalLabels, setEvalLabels] = useState('normal'); // 'normal' | 'defect' | 'mixed'
  const [evaluating, setEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState(null);
  const [evalError, setEvalError] = useState(null);

  // Load profiles
  const loadProfiles = async () => {
    setLoading(true);
    try {
      const data = await api.getProductionProfiles();
      if (data?.profiles) {
        setProfiles(data.profiles);
      }
    } catch (err) {
      console.error('Failed to load profiles:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfiles();
  }, []);

  // Actions
  const handleActivate = async (profileId) => {
    try {
      await api.activateProfile(profileId);
      await loadProfiles();
    } catch (err) {
      alert(`Failed to activate profile: ${err.message || err}`);
    }
  };

  const handleDeactivate = async (profileId) => {
    try {
      await api.deactivateProfile(profileId);
      await loadProfiles();
    } catch (err) {
      alert(`Failed to deactivate profile: ${err.message || err}`);
    }
  };

  const handleArchive = async (profileId) => {
    if (!window.confirm(`Archive profile "${profileId}"? It will be unloaded from active memory.`)) return;
    try {
      await api.archiveProfile(profileId);
      await loadProfiles();
    } catch (err) {
      alert(`Failed to archive profile: ${err.message || err}`);
    }
  };

  const handleDelete = async (profileId) => {
    if (!window.confirm(`PERMANENTLY delete profile "${profileId}" and its memory bank files? This cannot be undone.`)) return;
    try {
      await api.deleteProfile(profileId);
      await loadProfiles();
    } catch (err) {
      alert(`Failed to delete profile: ${err.message || err}`);
    }
  };

  const handleOpenAnalytics = async (profileId) => {
    try {
      const data = await api.getProfileAnalytics(profileId);
      setSelectedAnalytics(data);
      setShowAnalyticsModal(true);
    } catch (err) {
      alert(`Failed to load profile analytics: ${err.message || err}`);
    }
  };

  // Wizard file handling
  const handleFilesSelected = (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    setSelectedFiles((prev) => [...prev, ...files]);
    const newPreviews = files.map((f) => URL.createObjectURL(f));
    setFilePreviews((prev) => [...prev, ...newPreviews]);
  };

  const handleRemoveFile = (idx) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== idx));
    setFilePreviews((prev) => {
      URL.revokeObjectURL(prev[idx]);
      return prev.filter((_, i) => i !== idx);
    });
  };

  const handleRunBuild = async () => {
    setWizardError(null);
    setWizardProgress('Screening optical quality of reference images...');
    try {
      const fd = new FormData();
      fd.append('product_name', productName || 'Adapted Product');
      fd.append('sku', sku || 'SKU-ADAPT-001');
      fd.append('category', category);
      fd.append('camera_id', camera);
      fd.append('lighting_profile', lighting);
      fd.append('acquisition_type', acquisition);
      fd.append('calibration_split_ratio', calibrationRatio);
      fd.append('coreset_ratio', coresetRatio);

      selectedFiles.forEach((file) => {
        fd.append('files', file);
      });

      setWizardProgress('Extracting ResNet18 patch embeddings & subsampling coreset...');
      const res = await api.adaptProductProfile(fd);
      setWizardProgress('Calibrating provisional decision threshold & verifying FAISS index...');
      setWizardResult(res);
      setWizardStep(4);
      await loadProfiles();
    } catch (err) {
      setWizardError(err.message || 'Failed to build product profile.');
      setWizardProgress('');
    }
  };

  const resetWizard = () => {
    setWizardStep(1);
    setProductName('');
    setSku('');
    setCategory('bottle');
    setCamera('CAM-EXT-01');
    setStation('Station 01 — Optical Quality');
    setLighting('ambient_or_diffuse');
    setAcquisition('controlled_photography');
    setSelectedFiles([]);
    filePreviews.forEach((url) => URL.revokeObjectURL(url));
    setFilePreviews([]);
    setWizardProgress('');
    setWizardError(null);
    setWizardResult(null);
    setShowWizard(false);
  };

  // Evaluation handling
  const handleRunEvaluate = async () => {
    if (!evalFiles.length) {
      setEvalError('Please select at least 1 image for evaluation.');
      return;
    }
    setEvaluating(true);
    setEvalError(null);
    try {
      const fd = new FormData();
      evalFiles.forEach((f) => fd.append('files', f));
      if (evalLabels !== 'mixed') {
        const labelsArr = evalFiles.map(() => evalLabels.toUpperCase());
        fd.append('labels', labelsArr.join(','));
      }
      const res = await api.evaluateProfile(evaluateProfileId, fd);
      setEvalResult(res);
    } catch (err) {
      setEvalError(err.message || 'Evaluation failed.');
    } finally {
      setEvaluating(false);
    }
  };

  // Filter profiles
  const filteredProfiles = profiles.filter((p) => {
    const matchesSearch =
      (p.product_name && p.product_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (p.sku && p.sku.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (p.profile_id && p.profile_id.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus =
      statusFilter === 'all' ||
      (statusFilter === 'active' && p.status === 'active') ||
      (statusFilter === 'inactive' && p.status === 'inactive') ||
      (statusFilter === 'archived' && p.status === 'archived') ||
      (statusFilter === 'provisional' && p.is_provisional);
    const matchesCategory = categoryFilter === 'all' || p.category === categoryFilter;
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const categories = Array.from(new Set(profiles.map((p) => p.category))).filter(Boolean);

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="p-1.5 rounded-lg bg-gradient-to-tr from-violet-600/30 to-cyan-500/30 border border-violet-500/30 text-cyan-400">
              <Boxes className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-bold font-heading text-white tracking-tight">
              Product Profiles & Domain Adaptation
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-violet-500/20 text-violet-300 border border-violet-500/40">
              Few-Shot PatchCore
            </span>
          </div>
          <p className="text-sm text-slate-400 max-w-2xl">
            Target-domain optical inspection profiles calibrated on product-specific defect-free specimens (K=5..20).
            Preserves frozen ResNet-18 features with isolated memory-bank training and held-out threshold calibration.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={loadProfiles}
            disabled={loading}
            className="p-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
            title="Refresh Profiles"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>

          <button
            type="button"
            onClick={() => setShowWizard(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-white font-medium text-xs shadow-lg shadow-violet-900/20 transition-all cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Create Adapted Profile</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
            Total Profiles
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white font-mono">{profiles.length}</span>
            <span className="text-[10px] text-slate-400">registered</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[11px] font-mono text-emerald-400/80 uppercase tracking-wider block mb-1">
            Active Routing
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-emerald-300 font-mono">
              {profiles.filter((p) => p.status === 'active').length}
            </span>
            <span className="text-[10px] text-slate-400">ready</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[11px] font-mono text-violet-400/80 uppercase tracking-wider block mb-1">
            Provisional Few-Shot
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-violet-300 font-mono">
              {profiles.filter((p) => p.is_provisional).length}
            </span>
            <span className="text-[10px] text-slate-400">adapted</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[11px] font-mono text-cyan-400/80 uppercase tracking-wider block mb-1">
            Archived Profiles
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-cyan-300 font-mono">
              {profiles.filter((p) => p.status === 'archived').length}
            </span>
            <span className="text-[10px] text-slate-400">dormant</span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3 rounded-xl bg-slate-950/40 border border-slate-800/60">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by SKU, Product or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Status:</span>
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive Only</option>
            <option value="provisional">Provisional Only</option>
            <option value="archived">Archived Only</option>
          </select>

          {categories.length > 0 && (
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50"
            >
              <option value="all">All Categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c.toUpperCase()}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Profiles Grid */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-slate-500 gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
          <span className="text-xs font-mono">Loading registered production profiles...</span>
        </div>
      ) : filteredProfiles.length === 0 ? (
        <div className="py-16 text-center rounded-2xl bg-slate-950/40 border border-dashed border-slate-800/80 p-8">
          <Boxes className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white mb-1">No production profiles match your criteria</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto mb-4">
            Create an adapted profile for a new manufacturing specimen or reset your search filters.
          </p>
          <button
            type="button"
            onClick={() => setShowWizard(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-xs font-medium transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Create Profile Now</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-5">
          {filteredProfiles.map((p) => {
            const isActive = p.status === 'active';
            const isArchived = p.status === 'archived';
            const isProvisional = p.is_provisional;

            return (
              <div
                key={p.profile_id}
                className={`rounded-2xl border transition-all p-5 flex flex-col justify-between ${
                  isArchived
                    ? 'bg-slate-950/40 border-slate-800/60 opacity-70'
                    : isActive
                    ? 'bg-slate-950/70 border-slate-800 hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-950/20'
                    : 'bg-slate-950/50 border-amber-500/20'
                }`}
              >
                <div>
                  {/* Top Bar: SKU, Status Badge */}
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-900 border border-slate-700 text-cyan-300">
                          {p.sku || p.product_id}
                        </span>
                        <span className="text-[10px] font-mono uppercase text-slate-400">
                          {p.category} ({p.category_type})
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-white tracking-tight">
                        {p.product_name}
                      </h3>
                      <span className="text-[11px] font-mono text-slate-500">
                        ID: {p.profile_id}
                      </span>
                    </div>

                    <div className="flex flex-col items-end gap-1">
                      {isArchived ? (
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold bg-slate-800 text-slate-400 border border-slate-700">
                          ARCHIVED
                        </span>
                      ) : isActive ? (
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          ACTIVE
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/30">
                          INACTIVE
                        </span>
                      )}

                      {isProvisional && (
                        <span className="text-[9px] font-mono text-violet-300 bg-violet-950/60 px-1.5 py-0.5 rounded border border-violet-800/50">
                          FEW-SHOT PROVISIONAL
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Station, Camera & Hardware */}
                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 bg-slate-900/60 p-3 rounded-xl border border-slate-800/60 mb-4 font-mono">
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block">Station / Camera</span>
                      <span className="text-slate-200 truncate block">{p.camera_id || 'CAM-01'}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase block">Lighting Profile</span>
                      <span className="text-slate-200 truncate block">{p.lighting_profile || 'standard'}</span>
                    </div>
                  </div>

                  {/* Core Metrics */}
                  <div className="grid grid-cols-3 gap-2 text-center mb-4">
                    <div className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800/80">
                      <span className="text-[10px] font-mono text-slate-400 uppercase block mb-0.5">Threshold (τ)</span>
                      <span className="text-sm font-bold font-mono text-cyan-300">
                        {p.calibrated_threshold ? p.calibrated_threshold.toFixed(4) : 'N/A'}
                      </span>
                    </div>

                    <div className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800/80">
                      <span className="text-[10px] font-mono text-slate-400 uppercase block mb-0.5">Target FAR</span>
                      <span className="text-sm font-bold font-mono text-emerald-300">
                        {p.target_far ? `${(p.target_far * 100).toFixed(1)}%` : '< 1.0%'}
                      </span>
                    </div>

                    <div className="p-2.5 rounded-xl bg-slate-900/40 border border-slate-800/80">
                      <span className="text-[10px] font-mono text-slate-400 uppercase block mb-0.5">Coreset Bank</span>
                      <span className="text-sm font-bold font-mono text-violet-300">
                        {p.coreset_vectors_count ? `${p.coreset_vectors_count} vecs` : 'FAISS Ready'}
                      </span>
                    </div>
                  </div>

                  {/* Notice/Disclaimer */}
                  {p.disclaimer && (
                    <div className="p-2.5 rounded-lg bg-violet-950/20 border border-violet-900/40 text-[11px] text-violet-200/80 mb-4 flex items-start gap-2">
                      <Info className="w-3.5 h-3.5 text-violet-400 shrink-0 mt-0.5" />
                      <span className="leading-snug">{p.disclaimer}</span>
                    </div>
                  )}
                </div>

                {/* Card Action Buttons */}
                <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    {onSelectProfileForInspect && (
                      <button
                        type="button"
                        onClick={() => onSelectProfileForInspect(p.profile_id)}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold transition-all cursor-pointer"
                        title="Route live inspection to this profile"
                      >
                        <Play className="w-3.5 h-3.5 fill-cyan-400 text-cyan-400" />
                        <span>Inspect</span>
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={() => handleOpenAnalytics(p.profile_id)}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-medium transition-all"
                      title="Inspect model analytics & score distribution"
                    >
                      <BarChart2 className="w-3.5 h-3.5 text-violet-400" />
                      <span>Analytics</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        setEvaluateProfileId(p.profile_id);
                        setShowEvaluateModal(true);
                      }}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-medium transition-all"
                      title="Evaluate test images on this profile"
                    >
                      <FileCheck className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Evaluate</span>
                    </button>
                  </div>

                  <div className="flex items-center gap-1">
                    {isActive ? (
                      <button
                        type="button"
                        onClick={() => handleDeactivate(p.profile_id)}
                        className="p-1.5 rounded-lg bg-slate-900 hover:bg-amber-500/20 text-slate-400 hover:text-amber-300 border border-slate-800 transition-colors"
                        title="Deactivate profile"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleActivate(p.profile_id)}
                        className="p-1.5 rounded-lg bg-slate-900 hover:bg-emerald-500/20 text-slate-400 hover:text-emerald-400 border border-slate-800 transition-colors"
                        title="Activate profile"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      </button>
                    )}

                    {!isArchived && (
                      <button
                        type="button"
                        onClick={() => handleArchive(p.profile_id)}
                        className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 transition-colors"
                        title="Archive profile"
                      >
                        <Archive className="w-3.5 h-3.5" />
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={() => handleDelete(p.profile_id)}
                      className="p-1.5 rounded-lg bg-slate-900 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 border border-slate-800 transition-colors"
                      title="Delete profile"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ========================================================================= */}
      {/* CREATE ADAPTED PROFILE MULTI-STEP WIZARD MODAL */}
      {/* ========================================================================= */}
      {showWizard && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-3xl rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-6 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div className="flex items-center gap-2.5">
                <span className="p-2 rounded-xl bg-violet-600/20 border border-violet-500/30 text-violet-400">
                  <Sparkles className="w-5 h-5" />
                </span>
                <div>
                  <h2 className="text-lg font-bold text-white font-heading">
                    Few-Shot Product Profile Adaptation Wizard
                  </h2>
                  <span className="text-xs text-slate-400">
                    Step {wizardStep} of 4 — {wizardStep === 1 ? 'Product & Hardware' : wizardStep === 2 ? 'Reference Images' : wizardStep === 3 ? 'Calibration Settings' : 'Profile Registered'}
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={resetWizard}
                className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Error Message */}
            {wizardError && (
              <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs mb-6 flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="block font-semibold">Adaptation Error</strong>
                  <span>{wizardError}</span>
                </div>
              </div>
            )}

            {/* Wizard Step 1: Product & Station Info */}
            {wizardStep === 1 && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Product Name <span className="text-rose-400">*</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Pharmaceutical Glass Vial 20ml"
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Stock Keeping Unit (SKU) <span className="text-rose-400">*</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. SKU-VIAL-020"
                      value={sku}
                      onChange={(e) => setSku(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Parent Visual Category
                    </label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500/50"
                    >
                      <option value="bottle">Bottle (Rigid Glass/Plastic)</option>
                      <option value="capsule">Capsule (Pharma)</option>
                      <option value="pill">Pill (Solid Tablet)</option>
                      <option value="cable">Cable / Wire</option>
                      <option value="hazelnut">Nut / Organic</option>
                      <option value="metal_nut">Metal Fastener</option>
                      <option value="screw">Screw / Bolt</option>
                      <option value="toothbrush">Toothbrush</option>
                      <option value="transistor">Electronic Component</option>
                      <option value="zipper">Zipper / Fastener</option>
                      <option value="carpet">Carpet (Texture)</option>
                      <option value="grid">Grid (Pattern)</option>
                      <option value="leather">Leather (Surface)</option>
                      <option value="tile">Tile (Ceramic)</option>
                      <option value="wood">Wood (Grained Surface)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Camera ID / Serial
                    </label>
                    <input
                      type="text"
                      value={camera}
                      onChange={(e) => setCamera(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500/50"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Illumination Type
                    </label>
                    <select
                      value={lighting}
                      onChange={(e) => setLighting(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500/50"
                    >
                      <option value="ambient_or_diffuse">Ambient / Diffuse White</option>
                      <option value="diffuse_backlight_v1">Studio Backlight (Silhouette)</option>
                      <option value="ring_light_axial">Direct Ring Light / Axial</option>
                      <option value="darkfield_oblique">Darkfield Oblique Illumination</option>
                    </select>
                  </div>
                </div>

                <div className="pt-4 flex justify-end">
                  <button
                    type="button"
                    disabled={!productName.trim() || !sku.trim()}
                    onClick={() => setWizardStep(2)}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium text-xs transition-all cursor-pointer"
                  >
                    <span>Next: Upload References</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {/* Wizard Step 2: Upload Normal Reference Images */}
            {wizardStep === 2 && (
              <div className="space-y-5">
                <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-800/40 text-cyan-200/90 text-xs flex items-start gap-2.5">
                  <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <div>
                    <strong className="block font-semibold">Strict Reference Intake Contract</strong>
                    Upload between 2 and 20 defect-free normal images of <strong>{productName}</strong>.
                    The engine will automatically partition the images into training and calibration subsets.
                  </div>
                </div>

                {/* Dropzone */}
                <div className="p-6 rounded-2xl border-2 border-dashed border-slate-700 hover:border-violet-500/60 transition-all text-center bg-slate-950/40">
                  <Upload className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                  <p className="text-xs text-slate-300 font-medium mb-1">
                    Drop defect-free normal images here, or browse files
                  </p>
                  <span className="text-[10px] text-slate-500 block mb-3">
                    PNG, JPG, or WEBP up to 20MB per frame
                  </span>
                  <label className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 cursor-pointer transition-all">
                    <span>Select Images</span>
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleFilesSelected}
                      className="hidden"
                    />
                  </label>
                </div>

                {/* Previews */}
                {selectedFiles.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-400 mb-2 font-mono">
                      <span>{selectedFiles.length} images selected</span>
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedFiles([]);
                          filePreviews.forEach((u) => URL.revokeObjectURL(u));
                          setFilePreviews([]);
                        }}
                        className="text-rose-400 hover:underline"
                      >
                        Clear All
                      </button>
                    </div>

                    <div className="grid grid-cols-4 sm:grid-cols-6 gap-2 max-h-48 overflow-y-auto p-2 rounded-xl bg-slate-950 border border-slate-800">
                      {filePreviews.map((url, i) => (
                        <div key={i} className="relative group rounded-lg overflow-hidden border border-slate-800 aspect-square">
                          <img src={url} alt={`ref-${i}`} className="w-full h-full object-cover" />
                          <button
                            type="button"
                            onClick={() => handleRemoveFile(i)}
                            className="absolute top-1 right-1 p-1 rounded bg-black/70 hover:bg-rose-600 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="pt-4 flex items-center justify-between">
                  <button
                    type="button"
                    onClick={() => setWizardStep(1)}
                    className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    disabled={selectedFiles.length < 2}
                    onClick={() => setWizardStep(3)}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium text-xs transition-all cursor-pointer"
                  >
                    <span>Next: Calibration Settings</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {/* Wizard Step 3: Calibration Split & Build */}
            {wizardStep === 3 && (
              <div className="space-y-5">
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-4">
                  <div>
                    <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1.5">
                      <span>Held-Out Calibration Split Ratio</span>
                      <span className="font-mono text-cyan-400">{(calibrationRatio * 100).toFixed(0)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0.20"
                      max="0.50"
                      step="0.05"
                      value={calibrationRatio}
                      onChange={(e) => setCalibrationRatio(parseFloat(e.target.value))}
                      className="w-full accent-cyan-500"
                    />
                    <span className="text-[10px] text-slate-400 block mt-1">
                      Separates ~{Math.max(1, Math.round(selectedFiles.length * (1 - calibrationRatio)))} images for memory bank and ~{Math.max(1, Math.round(selectedFiles.length * calibrationRatio))} images for held-out threshold calibration.
                    </span>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1.5">
                      <span>Coreset Subsampling Ratio</span>
                      <span className="font-mono text-violet-400">{(coresetRatio * 100).toFixed(0)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0.05"
                      max="0.25"
                      step="0.01"
                      value={coresetRatio}
                      onChange={(e) => setCoresetRatio(parseFloat(e.target.value))}
                      className="w-full accent-violet-500"
                    />
                    <span className="text-[10px] text-slate-400 block mt-1">
                      Minimax greedy subsampling fraction for the PatchCore resident memory bank.
                    </span>
                  </div>
                </div>

                {wizardProgress && (
                  <div className="p-4 rounded-xl bg-violet-950/30 border border-violet-800/40 text-violet-200 text-xs flex items-center gap-3 animate-pulse">
                    <RefreshCw className="w-4 h-4 text-violet-400 animate-spin shrink-0" />
                    <span>{wizardProgress}</span>
                  </div>
                )}

                <div className="pt-4 flex items-center justify-between">
                  <button
                    type="button"
                    disabled={!!wizardProgress}
                    onClick={() => setWizardStep(2)}
                    className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium"
                  >
                    Back
                  </button>
                  <button
                    type="button"
                    disabled={!!wizardProgress}
                    onClick={handleRunBuild}
                    className="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 disabled:opacity-50 text-white font-semibold text-xs shadow-lg shadow-violet-900/30 transition-all cursor-pointer"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>{wizardProgress ? 'Building Profile...' : 'Build & Register Profile'}</span>
                  </button>
                </div>
              </div>
            )}

            {/* Wizard Step 4: Success & Registration Summary */}
            {wizardStep === 4 && wizardResult && (
              <div className="space-y-5 text-center py-4">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/40">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white font-heading">
                    Profile Successfully Built and Registered!
                  </h3>
                  <span className="text-xs font-mono text-cyan-300">{wizardResult.profile_id}</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-left max-w-xl mx-auto">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs">
                    <span className="text-[10px] text-slate-500 block uppercase">Calibrated τ</span>
                    <strong className="text-cyan-300 text-sm">{wizardResult.calibrated_threshold.toFixed(4)}</strong>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs">
                    <span className="text-[10px] text-slate-500 block uppercase">Coreset Vectors</span>
                    <strong className="text-violet-300 text-sm">{wizardResult.coreset_vectors_count}</strong>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs">
                    <span className="text-[10px] text-slate-500 block uppercase">Training Samples</span>
                    <strong className="text-emerald-300 text-sm">{wizardResult.training_samples_count}</strong>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs">
                    <span className="text-[10px] text-slate-500 block uppercase">Held-Out Cal</span>
                    <strong className="text-amber-300 text-sm">{wizardResult.calibration_samples_count}</strong>
                  </div>
                </div>

                <div className="pt-4 flex items-center justify-center gap-3">
                  {onSelectProfileForInspect && (
                    <button
                      type="button"
                      onClick={() => {
                        onSelectProfileForInspect(wizardResult.profile_id);
                        resetWizard();
                      }}
                      className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition-all cursor-pointer"
                    >
                      <Play className="w-4 h-4 fill-white" />
                      <span>Inspect With This Profile</span>
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={resetWizard}
                    className="px-5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium"
                  >
                    Done
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* EVALUATION MODAL */}
      {/* ========================================================================= */}
      {showEvaluateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-2xl rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
              <div className="flex items-center gap-2.5">
                <FileCheck className="w-5 h-5 text-emerald-400" />
                <div>
                  <h2 className="text-base font-bold text-white">Evaluate Profile: {evaluateProfileId}</h2>
                  <span className="text-xs text-slate-400">Score test images and compute empirical verification metrics</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => {
                  setShowEvaluateModal(false);
                  setEvalResult(null);
                  setEvalFiles([]);
                  setEvalError(null);
                }}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {evalError && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs mb-4">
                {evalError}
              </div>
            )}

            {!evalResult ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Select Test Images
                  </label>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={(e) => setEvalFiles(Array.from(e.target.files || []))}
                    className="w-full text-xs text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-slate-800 file:text-slate-200 file:text-xs"
                  />
                  <span className="text-[10px] text-slate-500 mt-1 block">
                    {evalFiles.length} test images selected
                  </span>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Ground-Truth Label Assumption
                  </label>
                  <select
                    value={evalLabels}
                    onChange={(e) => setEvalLabels(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white"
                  >
                    <option value="normal">All uploaded images are NORMAL</option>
                    <option value="defect">All uploaded images are DEFECTIVE</option>
                    <option value="mixed">Unlabeled (Score distribution only)</option>
                  </select>
                </div>

                <div className="pt-3 flex justify-end">
                  <button
                    type="button"
                    disabled={evaluating || !evalFiles.length}
                    onClick={handleRunEvaluate}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs cursor-pointer transition-all"
                  >
                    {evaluating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
                    <span>{evaluating ? 'Evaluating...' : 'Run Test Evaluation'}</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">Accuracy</span>
                    <strong className="text-emerald-400 text-base font-mono">
                      {evalResult.metrics?.accuracy !== undefined ? `${(evalResult.metrics.accuracy * 100).toFixed(1)}%` : 'N/A'}
                    </strong>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">Precision</span>
                    <strong className="text-cyan-400 text-base font-mono">
                      {evalResult.metrics?.precision !== undefined ? `${(evalResult.metrics.precision * 100).toFixed(1)}%` : 'N/A'}
                    </strong>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">Recall</span>
                    <strong className="text-violet-400 text-base font-mono">
                      {evalResult.metrics?.recall !== undefined ? `${(evalResult.metrics.recall * 100).toFixed(1)}%` : 'N/A'}
                    </strong>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block uppercase">F1 Score</span>
                    <strong className="text-amber-400 text-base font-mono">
                      {evalResult.metrics?.f1_score !== undefined ? evalResult.metrics.f1_score.toFixed(4) : 'N/A'}
                    </strong>
                  </div>
                </div>

                <div className="max-h-60 overflow-y-auto border border-slate-800 rounded-xl bg-slate-950 p-2 font-mono text-[11px]">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-500">
                        <th className="p-1.5">File</th>
                        <th className="p-1.5">Score</th>
                        <th className="p-1.5">Verdict</th>
                        <th className="p-1.5">Correct?</th>
                      </tr>
                    </thead>
                    <tbody>
                      {evalResult.samples?.map((s, idx) => (
                        <tr key={idx} className="border-b border-slate-900/60 text-slate-300">
                          <td className="p-1.5 truncate max-w-[120px]">{s.filename}</td>
                          <td className="p-1.5 text-cyan-300">{s.anomaly_score}</td>
                          <td className="p-1.5 font-bold">
                            <span className={s.verdict === 'DEFECTIVE' ? 'text-rose-400' : 'text-emerald-400'}>
                              {s.verdict}
                            </span>
                          </td>
                          <td className="p-1.5">
                            {s.is_correct === true ? (
                              <span className="text-emerald-400">YES</span>
                            ) : s.is_correct === false ? (
                              <span className="text-rose-400">NO</span>
                            ) : (
                              <span className="text-slate-500">—</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="pt-3 flex justify-end">
                  <button
                    type="button"
                    onClick={() => setEvalResult(null)}
                    className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium"
                  >
                    Evaluate Another Batch
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* ANALYTICS MODAL */}
      {/* ========================================================================= */}
      {showAnalyticsModal && selectedAnalytics && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-2xl rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
              <div className="flex items-center gap-2.5">
                <BarChart2 className="w-5 h-5 text-violet-400" />
                <h2 className="text-base font-bold text-white">Profile Analytics: {selectedAnalytics.profile_id}</h2>
              </div>
              <button
                type="button"
                onClick={() => setShowAnalyticsModal(false)}
                className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-4 text-xs font-mono">
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-slate-500 uppercase block font-semibold text-[10px]">Held-Out Score Distribution</span>
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 text-slate-200">
                  <div>Mean: <strong className="text-cyan-300">{selectedAnalytics.score_metrics?.mean || 'N/A'}</strong></div>
                  <div>Std: <strong className="text-cyan-300">{selectedAnalytics.score_metrics?.std || 'N/A'}</strong></div>
                  <div>P50: <strong className="text-cyan-300">{selectedAnalytics.score_metrics?.p50 || 'N/A'}</strong></div>
                  <div>P90: <strong className="text-cyan-300">{selectedAnalytics.score_metrics?.p90 || 'N/A'}</strong></div>
                  <div>P95: <strong className="text-cyan-300">{selectedAnalytics.score_metrics?.p95 || 'N/A'}</strong></div>
                  <div>P99: <strong className="text-cyan-300">{selectedAnalytics.score_metrics?.p99 || 'N/A'}</strong></div>
                  <div>Max: <strong className="text-cyan-300">{selectedAnalytics.score_metrics?.max || 'N/A'}</strong></div>
                  <div>Threshold: <strong className="text-emerald-400">{selectedAnalytics.calibrated_threshold}</strong></div>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-slate-500 uppercase block font-semibold text-[10px]">FAISS Memory Bank Artifacts</span>
                <div className="grid grid-cols-2 gap-2 text-slate-300">
                  <div>Coreset Vectors: <strong>{selectedAnalytics.memory_bank?.vectors}</strong></div>
                  <div>Dimension: <strong>{selectedAnalytics.memory_bank?.feature_dimension}D (ResNet18)</strong></div>
                  <div>Coreset Ratio: <strong>{(selectedAnalytics.memory_bank?.coreset_ratio * 100).toFixed(0)}%</strong></div>
                  <div>Index: <strong>IndexFlatL2</strong></div>
                </div>
              </div>

              {selectedAnalytics.manifest?.artifacts && (
                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <span className="text-slate-500 uppercase block font-semibold text-[10px]">SHA-256 Checksums</span>
                  {Object.entries(selectedAnalytics.manifest.artifacts).map(([filename, meta]) => (
                    <div key={filename} className="text-[10px] text-slate-400">
                      <strong className="text-slate-200 block">{filename}</strong>
                      <span className="text-cyan-500 truncate block">{meta.sha256}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
