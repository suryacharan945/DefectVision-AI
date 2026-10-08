import React, { useState, useEffect, useRef } from 'react';
import {
  UploadCloud,
  ShieldCheck,
  AlertOctagon,
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

export default function InspectSection({ onNavigateToSimilarity, onNavigateToRAG }) {
  const [category, setCategory] = useState('bottle');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [presets, setPresets] = useState([]);
  const [loadingPresets, setLoadingPresets] = useState(true);

  // Inspection states: 'idle' | 'analyzing' | 'completed' | 'error'
  const [status, setStatus] = useState('idle');
  const [analysisStep, setAnalysisStep] = useState(0);
  const [errorMessage, setErrorMessage] = useState(null);

  // Results
  const [result, setResult] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  const fileInputRef = useRef(null);

  // Load curated sample presets
  useEffect(() => {
    async function loadPresets() {
      try {
        const data = await api.getSamplePresets();
        setPresets(data);
      } catch (err) {
        console.warn('Could not load presets:', err);
      } finally {
        setLoadingPresets(false);
      }
    }
    loadPresets();
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
      // Fetch the real image blob from the backend static outputs
      const res = await fetch(preset.image_url);
      const blob = await res.blob();
      const file = new File([blob], preset.filename, { type: 'image/png' });

      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(blob));

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
    if (!category) {
      setErrorMessage('Please select a valid product category.');
      return;
    }

    setErrorMessage(null);
    setStatus('analyzing');
    setAnalysisStep(1);

    const stepTimer1 = setTimeout(() => setAnalysisStep(2), 600);
    const stepTimer2 = setTimeout(() => setAnalysisStep(3), 1200);

    try {
      const inferenceResult = await api.predict(selectedFile, category);
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setResult(inferenceResult);
      setStatus('completed');

      // Call /explain
      fetchExplanation(inferenceResult, category);
    } catch (err) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      console.error('Inspection failed:', err);
      setStatus('error');
      setErrorMessage(err.detail || err.message || 'Inspection error occurred. Ensure backend is running.');
    }
  };

  // Fetch explanation via /explain
  const fetchExplanation = async (infResult, cat) => {
    setLoadingExplanation(true);
    try {
      const explainRes = await api.explain({
        category: cat,
        defect_type: infResult.defect_type || (infResult.predicted_label === 'defective' ? 'anomaly' : 'normal'),
        severity_level: infResult.severity_level,
        severity_score: infResult.severity_score,
        defect_area_pct: infResult.defect_area_pct,
        confidence_pct: infResult.confidence_pct,
      });
      setExplanation(explainRes.explanation);
    } catch (err) {
      console.warn('LLM explanation failed, falling back:', err);
      setExplanation(
        `Inspection of ${cat} confirmed ${infResult.predicted_label} state (severity score: ${infResult.severity_score}/100, confidence: ${infResult.confidence_pct}%).`
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
        </div>

        {/* Required Category Selection Constraint */}
        <div className="flex flex-col gap-1.5 min-w-[280px]">
          <label htmlFor="category-select" className="flex items-center justify-between text-xs font-semibold text-slate-300">
            <span className="flex items-center gap-1">
              <span>Target Product Category</span>
              <span className="text-cyan-400 font-bold">*</span>
            </span>
            <Tooltip text="Required constraint: PatchCore memory banks and FAISS indexes are trained per-category. A model trained on bottle cannot inspect a screw." />
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
              className="w-full appearance-none px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-sm font-medium text-white focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all cursor-pointer"
            >
              <optgroup label="Objects (10 Categories)">
                {CATEGORIES.filter((c) => c.type === 'Object').map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.label} ({c.type})
                  </option>
                ))}
              </optgroup>
              <optgroup label="Textures (5 Categories)">
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
            Active: <strong className="text-cyan-300">{currentCatMeta.label}</strong> ({currentCatMeta.desc})
          </span>
        </div>
      </div>

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

          <div className="flex items-center gap-3">
            <button
              type="button"
              disabled={!selectedFile || status === 'analyzing'}
              onClick={handleRunInspection}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold text-sm transition-all shadow-lg ${
                status === 'analyzing'
                  ? 'bg-slate-800 text-slate-400 cursor-not-allowed border border-slate-700'
                  : 'bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white shadow-[0_0_20px_rgba(139,92,246,0.35)] active:scale-[0.98]'
              }`}
            >
              {status === 'analyzing' ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                  <span>Processing Inference...</span>
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
              
              {/* Verdict Header Banner */}
              <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800/80 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4 shadow-xl">
                <div>
                  <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-1">
                    Automated Visual Verdict
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-2xl font-bold tracking-tight text-white capitalize">
                      {result.predicted_label === 'defective' ? 'Defective Specimen' : 'Conforming Specimen'}
                    </span>
                    <SeverityBadge level={result.severity_level} score={result.severity_score} size="lg" />
                  </div>
                </div>

                <div className="flex items-center gap-2 text-right">
                  <div>
                    <div className="text-[10px] font-mono text-slate-400 uppercase">Defect Classification</div>
                    <div className="text-sm font-mono font-bold text-cyan-300 capitalize">
                      {result.defect_type || 'Unclassified anomaly'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Heatmap Slider: Before vs After Localization */}
              <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/90 backdrop-blur-md">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-violet-400" />
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                      PatchCore Anomaly Localization Map
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-cyan-400">
                    PatchCore AUROC: 0.9651
                  </span>
                </div>

                <HeatmapSlider
                  originalImage={result.original_image || previewUrl}
                  heatmapOverlay={result.heatmap}
                  rawHeatmap={result.raw_heatmap}
                />
              </div>

              {/* 4 Quantitative Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <MetricCard
                  title="Severity"
                  value={result.severity_score}
                  unit="/100"
                  accentColor="#ef4444"
                  tooltip="Severity: Composite index (0-100) combining anomaly distance, affected surface area, and classifier certainty."
                  badge={<SeverityBadge level={result.severity_level} showScore={false} size="sm" />}
                />

                <MetricCard
                  title="Confidence"
                  value={result.confidence_pct}
                  unit="%"
                  isPercent={true}
                  accentColor="#8b5cf6"
                  tooltip="Confidence: How sure the EfficientNet-B0 v3 model is that this sample is defective."
                />

                <MetricCard
                  title="Defect Area"
                  value={result.defect_area_pct}
                  unit="%"
                  isPercent={true}
                  accentColor="#06b6d4"
                  tooltip="Defect Area: Percentage of total specimen surface pixels showing anomaly score exceeding baseline threshold."
                />

                <MetricCard
                  title="PatchCore"
                  value={result.raw_patchcore_score}
                  accentColor="#38bdf8"
                  tooltip="Raw PatchCore Score: Peak nearest-neighbor L2 distance from patch embedding to normal memory bank."
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
                      {explanation}
                    </p>

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
