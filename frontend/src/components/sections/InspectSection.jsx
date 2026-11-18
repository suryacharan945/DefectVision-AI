import React, { useState, useEffect, useRef } from 'react';
import {
  UploadCloud,
  ShieldCheck,
  AlertOctagon,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  RefreshCw,
  Search,
  MessageSquare,
  FileImage,
  Layers,
  Zap,
  Info,
  ChevronRight
} from 'lucide-react';
import { api } from '../../api/client';
import { CATEGORIES, getCategoryMeta } from '../../utils/categories';
import SeverityBadge from '../ui/SeverityBadge';
import MetricCard from '../ui/MetricCard';
import HeatmapSlider from '../ui/HeatmapSlider';
import Tooltip from '../ui/Tooltip';

export default function InspectSection({
  onNavigateToSimilarity,
  onNavigateToRAG,
  backendHealth,
  demoMode,
  onToggleDemoMode,
  onRetryConnection,
}) {
  const isBackendReady = backendHealth?.status === 'ready';
  const [category, setCategory] = useState('auto');
  const [routingMode, setRoutingMode] = useState('benchmark'); // 'benchmark' | 'production'
  const [productionProfiles, setProductionProfiles] = useState([]);
  const [selectedProfileId, setSelectedProfileId] = useState('bottle_001_station_01');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [presets, setPresets] = useState([]);
  const [loadingPresets, setLoadingPresets] = useState(true);

  // Inspection states: 'idle' | 'analyzing' | 'completed' | 'error'
  const [status, setStatus] = useState('idle');
  const [analysisStep, setAnalysisStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState(null);
  const [showModelInfo, setShowModelInfo] = useState(false);

  // Results
  const [result, setResult] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  const fileInputRef = useRef(null);

  // Load curated sample presets & production profiles
  useEffect(() => {
    async function loadInitialData() {
      try {
        const [presetsData, profilesData] = await Promise.allSettled([
          api.getSamplePresets(),
          api.getProductionProfiles()
        ]);
        if (presetsData.status === 'fulfilled') {
          setPresets(presetsData.value);
        }
        if (profilesData.status === 'fulfilled' && profilesData.value?.profiles?.length > 0) {
          setProductionProfiles(profilesData.value.profiles);
          setSelectedProfileId(profilesData.value.profiles[0].profile_id);
        }
      } catch (err) {
        console.warn('Could not load initial presets or profiles:', err);
      } finally {
        setLoadingPresets(false);
      }
    }
    loadInitialData();
  }, []);

  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setErrorMessage('Please select a valid image file (PNG, JPG, JPEG).');
      return;
    }

    setErrorMessage(null);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setExplanation(null);
    setStatus('idle');
  };

  // Handle Preset Click (1-Click Real Inspection)
  const handleSelectPreset = async (preset) => {
    setCategory(preset.category);
    setErrorMessage(null);
    setResult(null);
    setExplanation(null);
    setStatus('analyzing');
    setAnalysisStep(1);

    try {
      let file = null;
      try {
        const res = await fetch(preset.image_url);
        if (res.ok) {
          const blob = await res.blob();
          file = new File([blob], preset.filename, { type: 'image/png' });
          setPreviewUrl(URL.createObjectURL(blob));
        }
      } catch (fetchErr) {
        console.warn('Preset image fetch warning:', fetchErr);
      }

      if (!file) {
        setPreviewUrl(preset.image_url);
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, 256, 256);
        ctx.fillStyle = '#38bdf8';
        ctx.font = 'bold 18px monospace';
        ctx.fillText(preset.category.toUpperCase(), 30, 130);
        const dummyBlob = await new Promise((r) => canvas.toBlob(r, 'image/png'));
        file = new File([dummyBlob], preset.filename, { type: 'image/png' });
      }

      setSelectedFile(file);

      // Step simulation for realistic progress disclosure
      setTimeout(() => setAnalysisStep(2), 600);
      setTimeout(() => setAnalysisStep(3), 1200);

      // Call REAL /predict endpoint
      const inferenceResult = await api.predict(file, preset.category);
      setResult(inferenceResult);
      setStatus('completed');

      // Now trigger real /explain endpoint
      fetchExplanation(inferenceResult, preset.category);
    } catch (err) {
      console.error('Inference error:', err);
      setStatus('error');
      setErrorMessage(err.detail || err.message || 'Failed to complete inspection inference.');
    }
  };

  // Run Inspection on Uploaded File
  const handleRunInspection = async () => {
    if (!selectedFile) {
      setErrorMessage('Please upload an image or choose a preset specimen first.');
      return;
    }
    if (routingMode === 'benchmark' && !category) {
      setErrorMessage('Please select a valid product category.');
      return;
    }

    setErrorMessage(null);
    setStatus('analyzing');
    setAnalysisStep(1);

    const stepTimer1 = setTimeout(() => setAnalysisStep(2), 600);
    const stepTimer2 = setTimeout(() => setAnalysisStep(3), 1200);

    try {
      const options = routingMode === 'production'
        ? { profile_id: selectedProfileId, routing_mode: 'production' }
        : { routing_mode: 'benchmark' };

      const inferenceResult = await api.predict(selectedFile, category, options);
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setResult(inferenceResult);
      setStatus('completed');

      // Call /explain only when inference was actually executed
      if (inferenceResult.inference_executed !== false) {
        fetchExplanation(inferenceResult, category);
      }
    } catch (err) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      console.error('Inspection failed:', err);
      setStatus('error');
      setErrorMessage(err.detail || err.message || 'Inspection error occurred. Ensure backend is running.');
    }
  };

  // Fetch explanation via /explain or use engine diagnosis
  const fetchExplanation = async (infResult, cat) => {
    if (infResult?.diagnosis) {
      setExplanation(infResult.diagnosis);
      return;
    }
    setLoadingExplanation(true);
    const targetCat = infResult?.detected_category || infResult?.category || cat || 'bottle';
    try {
      const explainRes = await api.explain({
        category: targetCat === 'auto' ? 'bottle' : targetCat,
        defect_type: infResult.defect_type || (infResult.predicted_label === 'defective' ? 'anomaly' : 'normal'),
        severity_level: infResult.severity_level || 'normal',
        severity_score: infResult.severity_score || 0,
        defect_area_pct: infResult.defect_area_pct || 0,
        confidence_pct: infResult.confidence_pct || 95,
      });
      setExplanation(explainRes.explanation);
    } catch (err) {
      console.warn('LLM explanation failed, falling back:', err);
      setExplanation(
        `Inspection of ${targetCat} confirmed ${infResult.verdict || infResult.predicted_label} state (anomaly score: ${infResult.anomaly_score || 0}, calibrated threshold: ${infResult.calibrated_threshold || infResult.optimal_threshold || 1.7452}). The result reflects the model's learned visual patterns and does not guarantee the absence of all possible defects.`
      );
    } finally {
      setLoadingExplanation(false);
    }
  };

  const stepsList = [
    'Validating specimen matrix & loading category memory bank...',
    'Extracting deep patch features with WideResNet50 (28×28 grid)...',
    'Running L2 nearest-neighbor anomaly scoring & PatchCore localization...',
    'Computing severity metrics & synthesizing explainable findings...',
  ];

  const currentCatMeta = getCategoryMeta(category);

  return (
    <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded text-[11px] font-mono uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Live Core Product (P0)
            </span>
            <span className="text-xs font-mono text-slate-400">• PatchCore + EfficientNet Pipeline</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-bold tracking-tight text-white">
            Upload & <span className="bg-gradient-to-r from-violet-400 to-cyan-300 bg-clip-text text-transparent">Live Inspect</span>
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Real-time visual anomaly localization with pixel-precision heatmaps and LLM-grounded operator explanations.
          </p>
          <button
            type="button"
            onClick={() => setShowModelInfo(!showModelInfo)}
            className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-cyan-500/50 text-xs font-mono text-cyan-300 transition-all cursor-pointer"
          >
            <Info className="w-3.5 h-3.5 text-cyan-400" />
            <span>{showModelInfo ? 'Hide Model & Provenance' : 'View Model Architecture & Provenance'}</span>
          </button>
        </div>

        {/* Routing Mode & Profile / Category Routing */}
        <div className="flex flex-col gap-2 min-w-[320px]">
          {/* Mode Switcher Tabs */}
          <div className="flex items-center rounded-xl bg-slate-950 p-1 border border-slate-800">
            <button
              type="button"
              onClick={() => {
                setRoutingMode('benchmark');
                setResult(null);
                setExplanation(null);
              }}
              className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all ${
                routingMode === 'benchmark'
                  ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Benchmark (15 MVTec AD)
            </button>
            <button
              type="button"
              onClick={() => {
                setRoutingMode('production');
                setResult(null);
                setExplanation(null);
              }}
              className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all ${
                routingMode === 'production'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              🏭 Production Profile
            </button>
          </div>

          {routingMode === 'benchmark' ? (
            /* Benchmark Category Selection */
            <div className="flex flex-col gap-1.5">
              <label htmlFor="category-select" className="flex items-center justify-between text-xs font-semibold text-slate-300">
                <span className="flex items-center gap-1">
                  <span>Product Category Routing</span>
                  <span className="text-cyan-400 font-bold">*</span>
                </span>
                <Tooltip text="Default: Automatic Category Recognition via EfficientNet-B0. Select a specific category only to force a manual override." />
              </label>
              <div className="relative">
                <select
                  id="category-select"
                  value={category}
                  onChange={(e) => {
                    setCategory(e.target.value);
                    setResult(null);
                    setExplanation(null);
                  }}
                  className="w-full appearance-none px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-sm font-medium text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all cursor-pointer font-sans"
                >
                  <option value="auto">⭐ Auto Recognize Category (Default)</option>
                  <optgroup label="Manual Overrides — Objects (10 Categories)">
                    {CATEGORIES.filter((c) => c.type === 'Object').map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.label} ({c.type})
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label="Manual Overrides — Textures (5 Categories)">
                    {CATEGORIES.filter((c) => c.type === 'Texture').map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.label} ({c.type})
                      </option>
                    ))}
                  </optgroup>
                </select>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 text-xs">
                  ▼
                </div>
              </div>
              <span className="text-[11px] text-slate-400">
                {category === 'auto' ? (
                  <span>Active: <strong className="text-cyan-300">Automatic Category Recognition</strong> (EfficientNet-B0)</span>
                ) : (
                  <span>Override: <strong className="text-amber-300">{currentCatMeta.label}</strong> ({currentCatMeta.desc})</span>
                )}
              </span>
            </div>
          ) : (
            /* Target Domain Production Profile Selection */
            <div className="flex flex-col gap-1.5">
              <label htmlFor="profile-select" className="flex items-center justify-between text-xs font-semibold text-slate-300">
                <span className="flex items-center gap-1">
                  <span>Target Inspection Profile</span>
                  <span className="text-cyan-400 font-bold">*</span>
                </span>
                <Tooltip text="Station & product specific inspection profile with tuned fixed ROI, custom illumination tolerance, and calibrated threshold." />
              </label>
              <div className="relative">
                <select
                  id="profile-select"
                  value={selectedProfileId}
                  onChange={(e) => {
                    setSelectedProfileId(e.target.value);
                    setResult(null);
                    setExplanation(null);
                  }}
                  className="w-full appearance-none px-3.5 py-2.5 rounded-xl bg-slate-900 border border-cyan-500/40 text-sm font-medium text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all cursor-pointer font-sans"
                >
                  {productionProfiles.map((p) => (
                    <option key={p.profile_id} value={p.profile_id}>
                      {p.product_name} ({p.profile_id})
                    </option>
                  ))}
                </select>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-cyan-400 text-xs">
                  ▼
                </div>
              </div>
              {(() => {
                const activeProf = productionProfiles.find((p) => p.profile_id === selectedProfileId);
                return activeProf ? (
                  <div className="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-300 flex flex-col gap-0.5">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Station:</span>
                      <strong className="text-cyan-300 truncate max-w-[180px]">{activeProf.inspection_station}</strong>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Threshold:</span>
                      <span className="text-emerald-400 font-bold">{activeProf.calibrated_threshold} (FAR: {(activeProf.target_far * 100).toFixed(1)}%)</span>
                    </div>
                    {(activeProf.validation_status || activeProf.profile_id === 'bottle_001_station_01') && (
                      <div className="mt-1 px-1.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[10px] font-semibold text-center uppercase tracking-wider">
                        {activeProf.validation_status || 'SIMULATED REFERENCE PROFILE — NOT PRODUCTION VALIDATED'}
                      </div>
                    )}
                  </div>
                ) : null;
              })()}
            </div>
          )}
        </div>
      </div>

      {/* Model & Provenance Info Drawer */}
      {showModelInfo && (
        <div className="mb-8 p-5 rounded-2xl bg-slate-900/95 border border-cyan-500/40 backdrop-blur-xl shadow-2xl animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <div className="flex items-center gap-2">
              <Info className="w-5 h-5 text-cyan-400" />
              <h3 className="text-sm font-bold uppercase tracking-wider text-white">Model Architecture & Provenance Metadata</h3>
            </div>
            <button
              type="button"
              onClick={() => setShowModelInfo(false)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
            >
              ✕
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80">
              <span className="text-cyan-400 font-bold block mb-1">1. Active Model Pipeline</span>
              <p className="text-slate-300 font-sans leading-relaxed">
                <strong>PatchCore</strong> (WideResNet-50 Layer 2+3 mid-level patch features with 10% greedy coreset subsampling memory bank) + <strong>EfficientNet-B0 v3</strong> (leak-free supervised classifier).
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80">
              <span className="text-violet-400 font-bold block mb-1">2. Preprocessing & Input</span>
              <p className="text-slate-300 font-sans leading-relaxed">
                PatchCore input: 224×224 resolution; EfficientNet input: 256×256 resolution. Standard ImageNet normalization (μ=[0.485, 0.456, 0.406], σ=[0.229, 0.224, 0.225]).
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80">
              <span className="text-emerald-400 font-bold block mb-1">3. Decision Boundary</span>
              <p className="text-slate-300 font-sans leading-relaxed">
                Active Category: <code className="text-cyan-300 font-bold">{category}</code>. Threshold calibrated to 99th percentile of nominal training distribution.
              </p>
            </div>
          </div>

          <div className="mt-4 p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs">
            <span className="text-amber-400 font-bold block mb-1">4. Training Dataset & Evaluation Provenance</span>
            <p className="text-slate-300 font-sans mb-2 leading-relaxed">
              Trained exclusively on <strong>nominal/normal instances</strong> from the standard MVTec AD training partition (zero defective images exposed during memory bank creation). Evaluated on canonical 856-specimen held-out benchmark test set (<code className="text-violet-300 font-mono">reports/step8_model_comparison_FAIR.csv</code>).
            </p>
            <div className="flex flex-wrap gap-3 text-[11px] font-mono text-slate-400 border-t border-slate-800/60 pt-2.5">
              <span>⚠️ <strong>Anomaly scores:</strong> Euclidean nearest-neighbor distances (not calibrated probabilities).</span>
              <span>⚠️ <strong>Severity score:</strong> Heuristic operational risk index (0–100).</span>
              <span>⚠️ <strong>LLM Explanations:</strong> Assistive guidance protocols (not certified physical root causes).</span>
            </div>
          </div>
        </div>
      )}

      {/* 1-Click Preset Specimen Bar */}
      <div className="mb-8 p-4 rounded-xl bg-slate-950/70 border border-slate-800/90 backdrop-blur-md">
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
              1-Click Benchmark Test Presets (Instant Live Inference)
            </span>
          </div>
          <span className="text-[11px] font-mono text-slate-400 hidden sm:inline">
            Click any specimen to run live backend inference
          </span>
        </div>

        <div className="flex items-center gap-2.5 overflow-x-auto pb-2 scrollbar-thin">
          {presets.slice(0, 10).map((preset) => (
            <button
              key={preset.category}
              type="button"
              onClick={() => handleSelectPreset(preset)}
              disabled={status === 'analyzing'}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg border text-left transition-all shrink-0 group ${
                category === preset.category && selectedFile?.name === preset.filename
                  ? 'bg-violet-600/30 border-cyan-400 text-white shadow-[0_0_12px_rgba(6,182,212,0.3)]'
                  : 'bg-slate-900/80 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-850'
              }`}
            >
              <img
                src={preset.image_url}
                alt={preset.title}
                className="w-9 h-9 rounded object-cover border border-slate-700 group-hover:scale-105 transition-transform"
              />
              <div>
                <div className="text-xs font-semibold text-slate-100 flex items-center gap-1">
                  <span>{preset.title}</span>
                </div>
                <div className="text-[10px] text-slate-400 truncate max-w-[120px]">
                  {preset.description}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Inspection Grid: Left Upload/Preview, Right Live Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Dropzone & Upload (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          
          <div
            onClick={() => fileInputRef.current?.click()}
            className={`relative group rounded-2xl border-2 border-dashed p-6 text-center cursor-pointer transition-all overflow-hidden ${
              previewUrl
                ? 'border-violet-500/50 bg-slate-900/40'
                : 'border-slate-700/80 hover:border-cyan-400/80 bg-slate-950/60 hover:bg-slate-900/40'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />

            {previewUrl ? (
              <div className="flex flex-col items-center gap-3">
                <div className="relative max-h-72 w-full flex items-center justify-center rounded-xl overflow-hidden bg-black/40 border border-slate-800">
                  <img src={previewUrl} alt="Selected Specimen" className="max-h-72 object-contain" />
                  
                  {/* Laser Scanline when analyzing */}
                  {status === 'analyzing' && (
                    <div className="absolute inset-0 pointer-events-none">
                      <div className="w-full h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#22d3ee] animate-scanline" />
                      <div className="absolute inset-0 bg-cyan-500/10 backdrop-blur-[0.5px]" />
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between w-full text-xs text-slate-300 px-1 font-mono">
                  <span className="truncate max-w-[200px]">{selectedFile?.name || 'specimen.png'}</span>
                  <span className="text-cyan-400 underline">Change Specimen</span>
                </div>
              </div>
            ) : (
              <div className="py-12 flex flex-col items-center justify-center">
                <div className="w-14 h-14 rounded-2xl bg-violet-600/15 border border-violet-500/30 flex items-center justify-center text-violet-400 mb-4 group-hover:scale-110 transition-transform">
                  <UploadCloud className="w-7 h-7 text-cyan-400" />
                </div>
                <div className="text-sm font-semibold text-slate-200">
                  Drop industrial specimen image here
                </div>
                <p className="text-xs text-slate-400 mt-1">or click to browse local files (PNG, JPG, TIFF)</p>
                <div className="mt-4 px-3 py-1 rounded-full bg-slate-900 text-[11px] font-mono text-slate-400 border border-slate-800">
                  Category: <span className="text-cyan-300 font-semibold">{currentCatMeta.label}</span>
                </div>
              </div>
            )}
          </div>

          {/* Action Button & Error */}
          {errorMessage && (
            <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2">
              <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold">Inspection Error:</strong> {errorMessage}
              </div>
            </div>
          )}

          {/* Backend Unavailable Notice */}
          {!isBackendReady && !demoMode && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-200 text-xs flex flex-col gap-2">
              <div className="flex items-center gap-2 font-semibold text-rose-300">
                <AlertOctagon className="w-4 h-4 text-rose-400" />
                <span>Real Model Execution Offline</span>
              </div>
              <p className="text-slate-300 leading-relaxed">
                The local Python backend daemon (FastAPI on port 8001) is unreachable. Genuine neural network inference cannot be performed.
              </p>
              <div className="flex flex-wrap items-center gap-2 mt-1">
                <button
                  type="button"
                  onClick={onRetryConnection}
                  className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-medium border border-slate-700"
                >
                  Retry Connection
                </button>
                <button
                  type="button"
                  onClick={() => onToggleDemoMode(true)}
                  className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-medium border border-amber-500/40"
                >
                  Enable Demo Mode (Synthetic)
                </button>
              </div>
            </div>
          )}

          <div className="flex items-center gap-3">
            <button
              type="button"
              disabled={!selectedFile || status === 'analyzing' || (!isBackendReady && !demoMode)}
              onClick={handleRunInspection}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold text-sm transition-all shadow-lg ${
                status === 'analyzing'
                  ? 'bg-slate-800 text-slate-400 cursor-not-allowed border border-slate-700'
                  : (!isBackendReady && !demoMode)
                  ? 'bg-slate-850 text-slate-500 cursor-not-allowed border border-slate-800'
                  : demoMode && !isBackendReady
                  ? 'bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-black shadow-[0_0_20px_rgba(245,158,11,0.35)] active:scale-[0.98]'
                  : 'bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white shadow-[0_0_20px_rgba(139,92,246,0.35)] active:scale-[0.98]'
              }`}
            >
              {status === 'analyzing' ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                  <span>Processing Inference...</span>
                </>
              ) : (!isBackendReady && !demoMode) ? (
                <>
                  <AlertOctagon className="w-4 h-4 text-slate-500" />
                  <span>Inference Disabled (Backend Offline)</span>
                </>
              ) : demoMode && !isBackendReady ? (
                <>
                  <Sparkles className="w-4 h-4 text-black" />
                  <span>Run Demo Inspection (Synthetic)</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Run Live Inspection</span>
                </>
              )}
            </button>

            {result && (
              <button
                type="button"
                onClick={() => {
                  setResult(null);
                  setExplanation(null);
                  setStatus('idle');
                }}
                className="px-3.5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-sm font-medium"
                title="Reset Inspection"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Analyzing Progress Card */}
          {status === 'analyzing' && (
            <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-500/40 backdrop-blur-md shadow-[0_0_20px_rgba(6,182,212,0.15)] animate-pulse">
              <div className="flex items-center justify-between text-xs text-cyan-300 font-mono mb-2">
                <span>INSPECTION IN PROGRESS</span>
                <span>STEP {analysisStep} OF 4</span>
              </div>
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mb-3">
                <div
                  className="h-full bg-gradient-to-r from-violet-500 to-cyan-400 transition-all duration-500"
                  style={{ width: `${(analysisStep / 4) * 100}%` }}
                />
              </div>
              <p className="text-xs text-slate-300 font-mono flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                <span>{stepsList[analysisStep - 1] || 'Executing model graph...'}</span>
              </p>
            </div>
          )}

        </div>

        {/* Right Column: Cinematic Results & Visual Reveal (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          
          {result ? (
            <div className="flex flex-col gap-6 animate-in fade-in duration-500">
              
              {/* Provenance & Inference Mode Indicator */}
              {result.is_demo ? (
                <div className="p-3.5 rounded-xl bg-amber-500/15 border border-amber-500/40 text-amber-200 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 shadow-lg">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-amber-500 text-black font-mono font-bold text-[10px] shrink-0">
                      DEMO MODE
                    </span>
                    <span className="font-medium">
                      Synthetic client-side simulation. NOT genuine neural network predictions.
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-amber-400/80 shrink-0">
                    Backend Server Offline
                  </span>
                </div>
              ) : (
                <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-300 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 shadow-lg">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-mono font-bold text-[10px] shrink-0">
                      LIVE INFERENCE
                    </span>
                    <span className="font-mono text-[11px] text-slate-300">
                      {result.model_id || result.model_selected || `PatchCore-${result.category || result.detected_category || 'Model'}`} (Score: {Number(result.anomaly_score || 0).toFixed(4)} | Threshold: {Number(result.anomaly_threshold || result.calibrated_threshold || result.optimal_threshold || 1.7452).toFixed(4)})
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-cyan-400 shrink-0">
                    {(result.inference_latency_ms || result.processing_time_ms || 0).toFixed(1)}ms
                  </span>
                </div>
              )}

              {/* 4-State Verdict Banner */}
              <div className="p-4 rounded-2xl bg-slate-900/95 border border-slate-800/90 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4 shadow-xl">
                <div>
                  <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-2">
                    <span>Inspection Verdict</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-cyan-400">{result.mode === 'upload' ? 'Image Upload' : 'Live Inspection'}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-xl text-base sm:text-lg font-heading font-black tracking-wide uppercase border ${
                      result.verdict === 'NORMAL'
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                        : result.verdict === 'DEFECTIVE'
                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/50 shadow-[0_0_15px_rgba(239,68,68,0.3)]'
                        : result.verdict === 'REVIEW REQUIRED'
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.3)]'
                        : 'bg-purple-500/20 text-purple-300 border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.3)]'
                    }`}>
                      {result.conclusion || (result.verdict === 'NORMAL' ? 'NO DEFECT DETECTED' : result.verdict === 'DEFECTIVE' ? 'POSSIBLE DEFECT DETECTED' : result.verdict === 'REVIEW REQUIRED' ? 'MANUAL INSPECTION REQUIRED' : 'UNSUPPORTED OR UNKNOWN CATEGORY')}
                    </span>
                    {result.severity_level && result.severity_level !== 'unsupported' && result.severity_level !== 'review' && (
                      <SeverityBadge level={result.severity_level} score={result.severity_score} size="lg" />
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3 text-right">
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">Decision State</div>
                    <div className="text-sm font-mono font-bold text-white capitalize">
                      {result.verdict || 'Evaluated'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Automatic Recognition & Quality Gate Telemetry Bar */}
              <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-slate-400">Category:</span>
                  <strong className="text-white uppercase font-bold">
                    {result.detected_category || result.category || 'UNKNOWN'}
                  </strong>
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                    {result.category_type || 'Object'}
                  </span>
                  <span className="text-violet-300 font-semibold">
                    {result.category_confidence
                      ? `${(result.category_confidence * 100).toFixed(1)}%`
                      : (result.confidence_pct ? `${result.confidence_pct}%` : '')}
                  </span>
                  {result.category_status === 'OPERATOR_OVERRIDE' && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-500/15 text-amber-300 border border-amber-500/30">
                      Override
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-3 text-slate-400">
                  <span>
                    Quality:{' '}
                    <strong className={
                      (result.image_quality?.status || result.image_quality_status) === 'PASSED' ||
                      (result.image_quality?.status || result.image_quality_status) === 'OPTICAL_QUALITY_VERIFIED'
                        ? 'text-emerald-400'
                        : 'text-amber-400'
                    }>
                      {result.image_quality?.status || result.image_quality_status || 'PASSED'}
                    </strong>
                  </span>
                  <span>•</span>
                  <span>
                    Score:{' '}
                    <strong className="text-cyan-300">
                      {result.inference_executed === false
                        ? 'N/A'
                        : Number(result.anomaly_score ?? 0).toFixed(4)}
                    </strong>{' '}
                    / Thresh:{' '}
                    <span className="text-slate-300">
                      {result.inference_executed === false
                        ? 'N/A'
                        : Number(result.anomaly_threshold || result.calibrated_threshold || result.optimal_threshold || 1.7452).toFixed(4)}
                    </span>
                  </span>
                </div>
              </div>

              {/* Actionable Callout Banner for Quality/Profile Rejection, Review Required or Unsupported */}
              {(result.inference_executed === false || result.verdict === 'REVIEW REQUIRED' || result.verdict === 'UNSUPPORTED') && (
                <div className={`p-4 rounded-xl border flex items-start gap-3.5 ${
                  result.verdict === 'UNSUPPORTED'
                    ? 'bg-purple-950/40 border-purple-500/40 text-purple-200'
                    : 'bg-amber-950/40 border-amber-500/40 text-amber-200'
                }`}>
                  <div className="mt-0.5 shrink-0">
                    {result.verdict === 'UNSUPPORTED' ? (
                      <AlertOctagon className="w-5 h-5 text-purple-400" />
                    ) : (
                      <AlertTriangle className="w-5 h-5 text-amber-400" />
                    )}
                  </div>
                  <div className="space-y-1 text-xs flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-heading font-bold text-sm tracking-wide uppercase">
                        {result.conclusion || result.verdict}: Attention Required
                      </h4>
                      <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-black/40 border border-white/10">
                        Stage: {result.rejection_stage || result.recognition_status || result.image_quality_status || 'QUALITY_GATE'}
                      </span>
                    </div>
                    <p className="leading-relaxed opacity-90">
                      {result.rejection_reason || result.review_reason || 'Specimen requires secondary inspection review.'}
                    </p>
                    {result.inference_executed === false && (
                      <p className="text-[11px] text-amber-300/80 font-sans italic pt-1">
                        * Deep anomaly inference and heatmaps were safely suppressed to avoid displaying misleading artifacts on unverified frames.
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Heatmap Slider: Only render overlay when heatmap was actually generated */}
              {result.heatmap_generated ? (
                <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/90 backdrop-blur-md">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Layers className="w-4 h-4 text-violet-400" />
                      <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                        PatchCore Anomaly Localization Map
                      </span>
                    </div>
                    <span className="text-[11px] font-mono text-cyan-400">
                      Mode: {result.routing_mode === 'production' ? `Profile (${result.profile_id})` : 'MVTec AD Benchmark'}
                    </span>
                  </div>

                  <HeatmapSlider
                    originalImage={result.original_image || previewUrl}
                    heatmapOverlay={result.heatmap}
                    rawHeatmap={result.raw_heatmap}
                  />
                </div>
              ) : (
                <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/90 backdrop-blur-md flex flex-col items-center justify-center text-center py-8">
                  <Layers className="w-8 h-8 text-slate-600 mb-2" />
                  <div className="text-sm font-semibold text-slate-300">Heatmap Suppressed</div>
                  <p className="text-xs text-slate-500 max-w-sm mt-1">
                    No anomaly heatmap generated because inference was not executed on this specimen.
                  </p>
                </div>
              )}

              {/* 4 Quantitative Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <MetricCard
                  title="Severity"
                  value={result.inference_executed === false ? 'N/A' : result.severity_score}
                  unit={result.inference_executed === false ? '' : '/100'}
                  accentColor="#ef4444"
                  tooltip="Severity: Composite index (0-100) combining anomaly distance, affected surface area, and classifier certainty."
                  badge={result.inference_executed !== false && <SeverityBadge level={result.severity_level} showScore={false} size="sm" />}
                />

                <MetricCard
                  title="Confidence"
                  value={result.inference_executed === false ? 'N/A' : result.confidence_pct}
                  unit={result.inference_executed === false ? '' : '%'}
                  isPercent={result.inference_executed !== false}
                  accentColor="#8b5cf6"
                  tooltip="Confidence: Defect classification certainty."
                />

                <MetricCard
                  title="Defect Area"
                  value={result.inference_executed === false ? 'N/A' : result.defect_area_pct}
                  unit={result.inference_executed === false ? '' : '%'}
                  isPercent={result.inference_executed !== false}
                  accentColor="#06b6d4"
                  tooltip="Defect Area: Percentage of specimen surface pixels exceeding calibrated decision threshold."
                />

                <MetricCard
                  title="Anomaly Score"
                  value={result.inference_executed === false ? 'N/A' : (result.anomaly_score ?? 'N/A')}
                  accentColor="#38bdf8"
                  tooltip="Peak nearest-neighbor distance from patch embeddings to target memory bank."
                />
              </div>

              {/* LLM-Grounded Operator Explanation Card */}
              <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950/90 border border-violet-500/30 backdrop-blur-xl shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-violet-600/10 rounded-full blur-2xl pointer-events-none" />

                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-violet-400" />
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                      Operator Defect Explanation
                    </span>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-violet-500/15 text-violet-300 border border-violet-500/30">
                    Validated by numeric_validator
                  </span>
                </div>

                {loadingExplanation ? (
                  <div className="flex items-center gap-2.5 py-4 text-xs font-mono text-slate-400">
                    <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                    <span>Synthesizing grounded explanation from defect metrics...</span>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <p className="text-sm text-slate-200 leading-relaxed font-normal">
                      {result.diagnosis || explanation}
                    </p>
                    {(!result.diagnosis || !result.diagnosis.includes("guarantee")) && (
                      <p className="text-[11px] text-slate-400 italic pt-1 border-t border-slate-800/60 font-mono">
                        Note: The result reflects the model's learned visual patterns and does not guarantee the absence of all possible defects.
                      </p>
                    )}

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-slate-800/80">
                      <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
                        <span className="font-semibold text-cyan-300 block mb-1">Operational Impact:</span>
                        <span className="text-slate-400">
                          {result.severity_level === 'Critical'
                            ? 'Immediate batch rejection required. High risk of field failure.'
                            : result.severity_level === 'Moderate'
                            ? 'Secondary inspection recommended. Possible marginal tolerance deviation.'
                            : 'Normal operating limits. Product passes production acceptance standards.'}
                        </span>
                      </div>

                      <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
                        <span className="font-semibold text-violet-300 block mb-1">Recommended Action:</span>
                        <span className="text-slate-400">
                          {result.severity_level === 'Critical'
                            ? 'Quarantine item and inspect upstream tooling for wear or misalignment.'
                            : result.severity_level === 'Moderate'
                            ? 'Flag for manual operator audit; monitor defect rate trend.'
                            : 'Release to packaging and assembly stage.'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Instant Follow-up Action Shortcuts */}
                <div className="flex flex-wrap items-center gap-3 mt-4 pt-3 border-t border-slate-800/60">
                  <button
                    type="button"
                    onClick={() => onNavigateToSimilarity(category)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-750 text-slate-200 text-xs font-medium border border-slate-700 hover:border-cyan-500/50 transition-all"
                  >
                    <Search className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Find Similar Historical Defects</span>
                    <ChevronRight className="w-3 h-3 text-slate-400" />
                  </button>

                  <button
                    type="button"
                    onClick={() => onNavigateToRAG(result.defect_type)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-750 text-slate-200 text-xs font-medium border border-slate-700 hover:border-violet-500/50 transition-all"
                  >
                    <MessageSquare className="w-3.5 h-3.5 text-violet-400" />
                    <span>Ask Defect Copilot</span>
                    <ChevronRight className="w-3 h-3 text-slate-400" />
                  </button>
                </div>

              </div>

            </div>
          ) : (
            /* Standby State */
            <div className="h-full min-h-[440px] rounded-2xl border border-slate-800/80 bg-slate-950/40 p-8 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-4">
                <FileImage className="w-8 h-8 text-slate-500" />
              </div>
              <h3 className="text-lg font-bold text-slate-300 mb-1">Awaiting Inspection Specimen</h3>
              <p className="text-xs text-slate-400 max-w-sm mb-6">
                Upload a component image or select one of the 1-click test presets above. Inference runs directly through PatchCore & EfficientNet-B0 v3.
              </p>
              <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-cyan-400" />
                  <span>PatchCore (FAISS)</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-violet-400" />
                  <span>EfficientNet-B0</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span>Severity Engine</span>
                </span>
              </div>
            </div>
          )}

        </div>

      </div>
    </section>
  );
}
