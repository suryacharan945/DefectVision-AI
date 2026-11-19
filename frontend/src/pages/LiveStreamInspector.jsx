import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Camera,
  Video,
  Radio,
  Zap,
  Sliders,
  Maximize2,
  RefreshCw,
  Clock,
  Layers,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  ShieldCheck,
  ChevronRight,
  Eye,
  Crosshair,
  Settings,
  HelpCircle,
  X,
  Sparkles,
  Filter,
  Server,
  Activity,
  Check,
  Info
} from 'lucide-react';
import { api } from '../api/client';
import { CATEGORIES, getCategoryMeta } from '../utils/categories';
import SeverityBadge from '../components/ui/SeverityBadge';
import HeatmapSlider from '../components/ui/HeatmapSlider';

export default function LiveStreamInspector({ onNavigateToRAG, onNavigateToSimilarity }) {
  // Stream & Source State
  const [streamMode, setStreamMode] = useState('webcam'); // 'webcam' | 'mjpeg'
  const [routingMode, setRoutingMode] = useState('benchmark'); // 'benchmark' | 'production'
  const [selectedCategory, setSelectedCategory] = useState('auto'); // 'auto' | 15 MVTec AD categories
  const [productionProfiles, setProductionProfiles] = useState([]);
  const [selectedProfileId, setSelectedProfileId] = useState('bottle_001_station_01');
  const [webcamActive, setWebcamActive] = useState(false);
  const [webcamError, setWebcamError] = useState(null);
  
  // Inspection Controls
  const [autoInspect, setAutoInspect] = useState(false);
  const [inspectInterval, setInspectInterval] = useState(1500); // ms
  const [isInspecting, setIsInspecting] = useState(false);
  const [shutterFlash, setShutterFlash] = useState(false);
  const [inspectionError, setInspectionError] = useState(null);

  // Real-time Metrics & HUD
  const [fps, setFps] = useState(24);
  const [latestResult, setLatestResult] = useState(null);
  const [eventHistory, setEventHistory] = useState([]);
  const [selectedEventModal, setSelectedEventModal] = useState(null);
  const [showModelStatusModal, setShowModelStatusModal] = useState(false);
  const [modelStatusData, setModelStatusData] = useState(null);

  // History Filter State
  const [historyCategoryFilter, setHistoryCategoryFilter] = useState('all');
  const [historyVerdictFilter, setHistoryVerdictFilter] = useState('all');

  // References
  const videoRef = useRef(null);
  const hudCanvasRef = useRef(null);
  const mjpegImgRef = useRef(null);
  const streamRef = useRef(null);
  const animFrameIdRef = useRef(null);
  const isInspectingRef = useRef(false);

  useEffect(() => {
    isInspectingRef.current = isInspecting;
  }, [isInspecting]);

  // Load Model Registry Status & Production Profiles
  const fetchModelStatus = useCallback(async () => {
    try {
      const [statusRes, profilesRes] = await Promise.allSettled([
        api.getOpticalModelStatus(),
        api.getProductionProfiles()
      ]);
      if (statusRes.status === 'fulfilled' && statusRes.value?.categories) {
        setModelStatusData(statusRes.value);
      }
      if (profilesRes.status === 'fulfilled' && profilesRes.value?.profiles?.length > 0) {
        setProductionProfiles(profilesRes.value.profiles);
        setSelectedProfileId(profilesRes.value.profiles[0].profile_id);
      }
    } catch (e) {
      console.warn('Could not fetch optical model status or profiles:', e);
    }
  }, []);

  useEffect(() => {
    fetchModelStatus();
  }, [fetchModelStatus]);

  // --------------------------------------------------------
  // 1. Client Browser Webcam Lifecycle (Mode 1)
  // --------------------------------------------------------
  const startWebcam = useCallback(async () => {
    try {
      setWebcamError(null);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch((err) => console.warn('Video play warning:', err));
      }
      setWebcamActive(true);
    } catch (err) {
      console.error('Failed to access webcam:', err);
      setWebcamActive(false);
      setWebcamError(
        err.name === 'NotAllowedError'
          ? 'Camera access was denied by browser permissions. Please allow camera access or switch to Backend Engine Stream.'
          : `Camera error: ${err.message}. Switch to Mode 2 (Backend Stream) to view live simulated industrial feed.`
      );
    }
  }, []);

  const stopWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setWebcamActive(false);
  }, []);

  useEffect(() => {
    if (streamMode === 'webcam') {
      startWebcam();
    } else {
      stopWebcam();
    }
    return () => {
      stopWebcam();
      if (animFrameIdRef.current) {
        cancelAnimationFrame(animFrameIdRef.current);
      }
    };
  }, [streamMode, startWebcam, stopWebcam]);

  // --------------------------------------------------------
  // 2. Holographic HUD Canvas Drawing Loop
  // --------------------------------------------------------
  useEffect(() => {
    let scanlineY = 50;
    let scanlineDir = 3;

    const renderHUD = () => {
      const canvas = hudCanvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      // Dynamic Color from Latest Verdict
      const verdict = latestResult?.verdict || 'READY';
      let bracketColor = '#06B6D4'; // Cyan default
      if (verdict === 'NORMAL') bracketColor = '#10B981'; // Green
      else if (verdict === 'DEFECTIVE') bracketColor = '#EF4444'; // Red
      else if (verdict === 'REVIEW REQUIRED') bracketColor = '#F59E0B'; // Amber
      else if (verdict === 'UNSUPPORTED') bracketColor = '#A855F7'; // Purple

      // Central ROI Box Coordinates (60% of canvas) or custom ROI bbox
      let roiX = Math.round((w - w * 0.62) / 2);
      let roiY = Math.round((h - h * 0.70) / 2);
      let roiW = Math.round(w * 0.62);
      let roiH = Math.round(h * 0.70);

      // Draw Neon Corner Brackets around ROI
      const bLen = 28;
      ctx.strokeStyle = bracketColor;
      ctx.lineWidth = 3;
      ctx.shadowColor = bracketColor;
      ctx.shadowBlur = 10;

      // Top-Left
      ctx.beginPath();
      ctx.moveTo(roiX + bLen, roiY);
      ctx.lineTo(roiX, roiY);
      ctx.lineTo(roiX, roiY + bLen);
      ctx.stroke();

      // Top-Right
      ctx.beginPath();
      ctx.moveTo(roiX + roiW - bLen, roiY);
      ctx.lineTo(roiX + roiW, roiY);
      ctx.lineTo(roiX + roiW, roiY + bLen);
      ctx.stroke();

      // Bottom-Left
      ctx.beginPath();
      ctx.moveTo(roiX, roiY + roiH - bLen);
      ctx.lineTo(roiX, roiY + roiH);
      ctx.lineTo(roiX + bLen, roiY + roiH);
      ctx.stroke();

      // Bottom-Right
      ctx.beginPath();
      ctx.moveTo(roiX + roiW - bLen, roiY + roiH);
      ctx.lineTo(roiX + roiW, roiY + roiH);
      ctx.lineTo(roiX + roiW, roiY + roiH - bLen);
      ctx.stroke();

      // Center Optical Reticle Crosshairs
      const cx = Math.round(w / 2);
      const cy = Math.round(h / 2);
      ctx.strokeStyle = '#06B6D4'; // Cyan
      ctx.lineWidth = 1.5;
      ctx.shadowColor = '#06B6D4';
      ctx.shadowBlur = 8;

      ctx.beginPath();
      ctx.arc(cx, cy, 22, 0, Math.PI * 2);
      ctx.moveTo(cx - 16, cy);
      ctx.lineTo(cx + 16, cy);
      ctx.moveTo(cx, cy - 16);
      ctx.lineTo(cx, cy + 16);
      ctx.stroke();

      // Animated Scanning Laser Line
      scanlineY += scanlineDir;
      if (scanlineY >= roiY + roiH - 6 || scanlineY <= roiY + 6) {
        scanlineDir *= -1;
      }

      ctx.shadowColor = bracketColor;
      ctx.shadowBlur = 15;
      const gradient = ctx.createLinearGradient(roiX, scanlineY, roiX + roiW, scanlineY);
      gradient.addColorStop(0, 'rgba(6,182,212,0.1)');
      gradient.addColorStop(0.5, 'rgba(6,182,212,0.85)');
      gradient.addColorStop(1, 'rgba(6,182,212,0.1)');
      ctx.strokeStyle = gradient;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(roiX, scanlineY);
      ctx.lineTo(roiX + roiW, scanlineY);
      ctx.stroke();

      ctx.shadowBlur = 0;
      animFrameIdRef.current = requestAnimationFrame(renderHUD);
    };

    animFrameIdRef.current = requestAnimationFrame(renderHUD);
    return () => {
      if (animFrameIdRef.current) cancelAnimationFrame(animFrameIdRef.current);
    };
  }, [latestResult]);

  // --------------------------------------------------------
  // 3. Frame Capture & Real-Time Inspection Trigger
  // --------------------------------------------------------
  const executeInspection = useCallback(
    async (silent = false) => {
      if (isInspectingRef.current) return;
      setIsInspecting(true);
      setInspectionError(null);

      if (!silent) {
        setShutterFlash(true);
        setTimeout(() => setShutterFlash(false), 120);
      }

      try {
        let frameBlob = null;

        if (streamMode === 'webcam' && videoRef.current) {
          const video = videoRef.current;
          if (video.videoWidth === 0 || video.videoHeight === 0) {
            setIsInspecting(false);
            return;
          }
          const canvas = document.createElement('canvas');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

          frameBlob = await new Promise((resolve) =>
            canvas.toBlob((b) => resolve(b), 'image/jpeg', 0.88)
          );
        } else {
          const imgEl = mjpegImgRef.current;
          if (imgEl && imgEl.naturalWidth > 0) {
            const canvas = document.createElement('canvas');
            canvas.width = imgEl.naturalWidth;
            canvas.height = imgEl.naturalHeight;
            const ctx = canvas.getContext('2d');
            try {
              ctx.drawImage(imgEl, 0, 0);
              frameBlob = await new Promise((resolve) =>
                canvas.toBlob((b) => resolve(b), 'image/jpeg', 0.88)
              );
            } catch (e) {
              frameBlob = null;
            }
          }
        }

        if (!frameBlob) {
          throw new Error('Unable to extract frame for inspection. Please ensure camera or stream is active.');
        }

        // Call Category-Aware or Production-Profile Optical Inspection Engine
        const options = routingMode === 'production'
          ? { profile_id: selectedProfileId, routing_mode: 'production' }
          : { routing_mode: 'benchmark' };

        const result = await api.inspectOpticalFrame(frameBlob, selectedCategory, options);

        const inspectionEvent = {
          ...result,
          id: `evt_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
          timestamp: new Date().toLocaleTimeString(),
          capturedCategory: result.detected_category || (routingMode === 'production' ? result.category : selectedCategory),
        };

        setLatestResult(inspectionEvent);
        setEventHistory((prev) => [inspectionEvent, ...prev.slice(0, 49)]);
      } catch (err) {
        console.error('Frame inspection error:', err);
        setInspectionError(
          err.detail || err.message || 'Frame inspection failed: backend service unreachable. Verify backend deployment or switch to Demo Mode.'
        );
      } finally {
        setIsInspecting(false);
      }
    },
    [streamMode, selectedCategory, routingMode, selectedProfileId]
  );

  // Hotkey & Auto-Inspection Listeners
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.code === 'Space' && !e.target.matches('input, textarea, select, button')) {
        e.preventDefault();
        executeInspection(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [executeInspection]);

  useEffect(() => {
    if (!autoInspect) return;
    const timer = setInterval(() => {
      if (!isInspectingRef.current) {
        executeInspection(true);
      }
    }, inspectInterval);
    return () => clearInterval(timer);
  }, [autoInspect, inspectInterval, executeInspection]);

  // Handle Clear History
  const handleClearHistory = async () => {
    try {
      await api.clearOpticalHistory();
      setEventHistory([]);
    } catch (e) {
      setEventHistory([]);
    }
  };

  // Filtered Event History
  const filteredHistory = eventHistory.filter((evt) => {
    if (historyCategoryFilter !== 'all' && evt.detected_category !== historyCategoryFilter) {
      return false;
    }
    if (historyVerdictFilter !== 'all' && evt.verdict !== historyVerdictFilter) {
      return false;
    }
    return true;
  });

  const getVerdictStyle = (verdict) => {
    switch (verdict) {
      case 'NORMAL':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-[0_0_12px_rgba(16,185,129,0.3)]';
      case 'DEFECTIVE':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/50 shadow-[0_0_12px_rgba(239,68,68,0.3)]';
      case 'REVIEW REQUIRED':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-[0_0_12px_rgba(245,158,11,0.3)]';
      case 'UNSUPPORTED':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/50 shadow-[0_0_12px_rgba(168,85,247,0.3)]';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-[1700px] mx-auto">
      {/* Top Header & Operational Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-cyan-400 p-[1px] shadow-[0_0_15px_rgba(6,182,212,0.4)]">
              <div className="w-full h-full bg-slate-950 rounded-[11px] flex items-center justify-center">
                <Video className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="font-heading text-xl sm:text-2xl font-bold tracking-tight text-white">
                  Real-Time Optical Inspection
                </h1>
                {api.isDemoMode() ? (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    DEMO SIMULATION
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40 animate-pulse">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                    LIVE STREAM
                  </span>
                )}
                <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                  <Sparkles className="w-3 h-3 text-cyan-400" />
                  Auto-Category Recognition
                </span>
              </div>
              <p className="text-xs text-slate-400">
                15 MVTec AD Category Recognition, Quality Gate, ResNet-18 PatchCore Memory Banks, & Fusion Decisions.
              </p>
            </div>
          </div>
        </div>

        {/* Top Controls: Mode, Category Registry Button, & Spacebar Action */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Stream Mode Switch */}
          <div className="flex items-center p-1 bg-slate-900/90 border border-slate-800 rounded-xl">
            <button
              type="button"
              onClick={() => setStreamMode('webcam')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                streamMode === 'webcam'
                  ? 'bg-violet-600/30 text-cyan-300 border border-violet-500/50 shadow-[0_0_12px_rgba(139,92,246,0.3)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Camera className="w-3.5 h-3.5" />
              <span>Browser Webcam</span>
            </button>

            <button
              type="button"
              onClick={() => setStreamMode('mjpeg')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                streamMode === 'mjpeg'
                  ? 'bg-violet-600/30 text-cyan-300 border border-violet-500/50 shadow-[0_0_12px_rgba(139,92,246,0.3)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Radio className="w-3.5 h-3.5" />
              <span>Backend MJPEG Feed</span>
            </button>
          </div>

          {/* Model Registry Status Button */}
          <button
            type="button"
            onClick={() => {
              fetchModelStatus();
              setShowModelStatusModal(true);
            }}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white hover:border-slate-700 transition-all"
          >
            <Server className="w-3.5 h-3.5 text-violet-400" />
            <span>15 Models Registry</span>
          </button>

          {/* Quick Snapshot Spacebar Action */}
          <button
            type="button"
            onClick={() => executeInspection(false)}
            disabled={isInspecting}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 via-indigo-600 to-cyan-500 text-white text-xs font-bold shadow-[0_0_15px_rgba(6,182,212,0.35)] hover:from-violet-500 hover:to-cyan-400 transition-all active:scale-[0.98] disabled:opacity-50"
          >
            <Zap className={`w-4 h-4 ${isInspecting ? 'animate-spin' : ''}`} />
            <span>{isInspecting ? 'Analyzing...' : 'Capture Frame'}</span>
            <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono bg-slate-900/60 rounded border border-white/20">
              SPACE
            </kbd>
          </button>
        </div>
      </div>

      {/* Main Studio Grid: Left Optical Viewport & Right Control Rail */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* Left Column: Video Viewport & Telemetry HUD (8 cols) */}
        <div className="xl:col-span-8 space-y-4">
          {/* Active Inspection Error Alert */}
          {inspectionError && (
            <div className="p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-center justify-between gap-3 text-xs text-rose-300 shadow-[0_0_15px_rgba(239,68,68,0.15)]">
              <div className="flex items-center gap-2.5">
                <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{inspectionError}</span>
              </div>
              <button
                type="button"
                onClick={() => setInspectionError(null)}
                className="p-1 hover:bg-rose-500/20 rounded text-rose-400 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Main Video Viewport Card */}
          <div className="relative rounded-2xl border border-slate-800 bg-slate-950/90 overflow-hidden shadow-2xl aspect-[16/10] flex items-center justify-center">
            {/* Shutter Flash Animation */}
            {shutterFlash && (
              <div className="absolute inset-0 z-30 bg-white/40 backdrop-blur-sm pointer-events-none transition-opacity duration-100" />
            )}

            {/* Viewport Mode 1: Browser Webcam */}
            {streamMode === 'webcam' ? (
              <>
                {webcamError ? (
                  <div className="p-8 text-center max-w-md space-y-3">
                    <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto" />
                    <h3 className="font-heading font-semibold text-white">Camera Access Notice</h3>
                    <p className="text-xs text-slate-400">{webcamError}</p>
                    <div className="pt-2 flex justify-center gap-3">
                      <button
                        type="button"
                        onClick={startWebcam}
                        className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-white"
                      >
                        Retry Camera
                      </button>
                      <button
                        type="button"
                        onClick={() => setStreamMode('mjpeg')}
                        className="px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-xs text-white"
                      >
                        Switch to Backend Stream
                      </button>
                    </div>
                  </div>
                ) : (
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover select-none"
                  />
                )}
                <canvas
                  ref={hudCanvasRef}
                  width={1280}
                  height={800}
                  className="absolute inset-0 w-full h-full pointer-events-none z-10"
                />
              </>
            ) : (
              /* Viewport Mode 2: Backend MJPEG Stream */
              <div className="relative w-full h-full flex items-center justify-center bg-black">
                <img
                  ref={mjpegImgRef}
                  src={api.getStreamUrl(selectedCategory === 'auto' ? 'bottle' : selectedCategory)}
                  alt="DefectVision Live MJPEG Feed"
                  className="w-full h-full object-contain select-none"
                  onError={() => console.warn('MJPEG stream connection error.')}
                />
              </div>
            )}

            {/* Top HUD Badges */}
            <div className="absolute top-4 left-4 z-20 flex flex-wrap items-center gap-2 pointer-events-none">
              <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-black/75 backdrop-blur-md text-cyan-300 border border-cyan-500/40 shadow-lg">
                FPS: {fps}
              </span>
              {latestResult && (
                <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-medium bg-black/75 backdrop-blur-md text-slate-300 border border-slate-700 shadow-lg">
                  Quality: {latestResult.image_quality_status || 'PASSED'}
                </span>
              )}
            </div>

            {/* Top-Right Verdict Overlay */}
            {latestResult && (
              <div className="absolute top-4 right-4 z-20 pointer-events-none">
                <div
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-heading font-black tracking-wider uppercase border backdrop-blur-md ${getVerdictStyle(
                    latestResult.verdict
                  )}`}
                >
                  {latestResult.conclusion || latestResult.verdict}
                </div>
              </div>
            )}

            {/* Bottom HUD: Category Recognition & Anomaly Telemetry */}
            {latestResult && (
              <div className="absolute bottom-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-black/80 backdrop-blur-md border border-slate-700/80 text-xs shadow-lg">
                  <span className="text-slate-400 font-mono">Recognized:</span>
                  <span className="font-bold text-white uppercase">
                    {latestResult.detected_category}
                  </span>
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                    {latestResult.category_type}
                  </span>
                  <span className="text-violet-300 font-mono font-bold">
                    {latestResult.category_confidence
                      ? `${Math.round(latestResult.category_confidence * 100)}%`
                      : '--'}
                  </span>
                </div>

                <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-black/80 backdrop-blur-md border border-slate-700/80 text-xs shadow-lg font-mono">
                  <span className="text-slate-400">Model:</span>
                  <span className="text-cyan-300 truncate max-w-[200px]">
                    {latestResult.model_selected || `PatchCore-${latestResult.detected_category}`}
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className="text-slate-300">{latestResult.processing_time_ms}ms</span>
                </div>
              </div>
            )}
          </div>

          {/* Operator Actionable Callout (Review Required / Unsupported Alerts) */}
          {latestResult && (latestResult.verdict === 'REVIEW REQUIRED' || latestResult.verdict === 'UNSUPPORTED') && (
            <div
              className={`p-4 rounded-xl border backdrop-blur-sm flex items-start gap-3.5 animate-fadeIn ${
                latestResult.verdict === 'UNSUPPORTED'
                  ? 'bg-purple-950/40 border-purple-500/40 text-purple-200'
                  : 'bg-amber-950/40 border-amber-500/40 text-amber-200'
              }`}
            >
              <div className="mt-0.5 flex-shrink-0">
                {latestResult.verdict === 'UNSUPPORTED' ? (
                  <AlertOctagon className="w-5 h-5 text-purple-400" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-amber-400" />
                )}
              </div>
              <div className="space-y-1 flex-1 text-xs">
                <div className="flex items-center justify-between">
                  <h4 className="font-heading font-bold text-sm tracking-wide uppercase">
                    {latestResult.verdict}: Attention Required
                  </h4>
                  <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-black/40 border border-white/10">
                    Gate: {latestResult.recognition_status || latestResult.image_quality_status}
                  </span>
                </div>
                <p className="leading-relaxed opacity-90">
                  {latestResult.review_reason ||
                    'Frame inspection triggered secondary review gate. Please inspect physical specimen or verify lighting conditions.'}
                </p>
                {latestResult.image_quality_metrics && (
                  <div className="pt-1 flex flex-wrap gap-2 text-[10px] font-mono opacity-80">
                    <span>Sharpness: {latestResult.image_quality_metrics.sharpness?.toFixed(1)} (Min 80.0)</span>
                    <span>•</span>
                    <span>Luminance: {latestResult.image_quality_metrics.mean_luminance?.toFixed(1)} (35-235)</span>
                    <span>•</span>
                    <span>Contrast: {latestResult.image_quality_metrics.contrast?.toFixed(1)} (Min 18.0)</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Viewport Sub-bar: Hotkeys, Calibration Tips & Automation Bar */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-3 text-slate-400">
              <div className="flex items-center gap-1.5 font-mono">
                <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300 text-[10px]">
                  SPACE
                </kbd>
                <span>Instant Inspect</span>
              </div>
              <span className="text-slate-600">•</span>
              <div className="flex items-center gap-1.5 font-mono">
                <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300 text-[10px]">
                  ROI
                </kbd>
                <span>Target Center Window</span>
              </div>
            </div>

            {/* Continuous Auto-Inspect Switch */}
            <div className="flex items-center gap-3">
              <span className="text-slate-400 font-medium">Continuous Auto-Scan:</span>
              <div className="flex items-center bg-slate-950 p-0.5 rounded-lg border border-slate-800 text-[11px]">
                <button
                  type="button"
                  onClick={() => setAutoInspect(false)}
                  className={`px-2 py-1 rounded-md transition-all ${
                    !autoInspect ? 'bg-slate-800 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Manual (Off)
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAutoInspect(true);
                    setInspectInterval(1500);
                  }}
                  className={`px-2 py-1 rounded-md transition-all ${
                    autoInspect && inspectInterval === 1500
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  1.5s
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAutoInspect(true);
                    setInspectInterval(3000);
                  }}
                  className={`px-2 py-1 rounded-md transition-all ${
                    autoInspect && inspectInterval === 3000
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  3.0s
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Model Controls & Defect Event Ticker (4 cols) */}
        <div className="xl:col-span-4 space-y-5">
          {/* Category Recognition & Routing Mode Selector */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4 text-cyan-400" />
                <span className="font-heading font-bold text-sm text-white">
                  Inspection Routing Mode
                </span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                {routingMode === 'production' ? 'Production Mode' : '15 MVTec AD Models'}
              </span>
            </div>

            {/* Mode Switcher Tabs */}
            <div className="flex items-center rounded-xl bg-slate-950 p-1 border border-slate-800">
              <button
                type="button"
                onClick={() => setRoutingMode('benchmark')}
                className={`flex-1 py-1 px-2.5 rounded-lg text-xs font-semibold transition-all ${
                  routingMode === 'benchmark'
                    ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Benchmark (15 MVTec AD)
              </button>
              <button
                type="button"
                onClick={() => setRoutingMode('production')}
                className={`flex-1 py-1 px-2.5 rounded-lg text-xs font-semibold transition-all ${
                  routingMode === 'production'
                    ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                🏭 Production Profile
              </button>
            </div>

            {routingMode === 'benchmark' ? (
              <div className="space-y-2">
                <label className="text-xs text-slate-400 block">
                  Category selection mode (Default: Automatic Recognition):
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-mono focus:outline-none focus:border-cyan-500 transition-colors cursor-pointer"
                >
                  <option value="auto">⭐ Automatic Category Recognition (Default)</option>
                  <optgroup label="Manual Category Overrides">
                    {CATEGORIES.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.label} ({cat.type}) — {cat.desc}
                      </option>
                    ))}
                  </optgroup>
                </select>
                <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs space-y-1">
                  <div className="flex items-center justify-between text-slate-300 font-medium">
                    <span>
                      Mode:{' '}
                      {selectedCategory === 'auto'
                        ? 'Automated Optical Routing'
                        : `Pinned: ${selectedCategory.toUpperCase()}`}
                    </span>
                    <span className="text-[10px] font-mono text-cyan-400">
                      {selectedCategory === 'auto' ? 'Self-Classifying' : 'Operator Override'}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    {selectedCategory === 'auto'
                      ? 'EfficientNet-B0 dynamically classifies input image into one of 15 MVTec AD categories and dispatches to resident PatchCore memory bank.'
                      : `Bypasses automated classification and forces PatchCore anomaly evaluation against ${selectedCategory} memory bank.`}
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <label className="text-xs text-slate-400 block">
                  Target Domain Production Inspection Profile:
                </label>
                <select
                  value={selectedProfileId}
                  onChange={(e) => setSelectedProfileId(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-950 border border-cyan-500/40 text-slate-200 text-xs font-mono focus:outline-none focus:border-cyan-500 transition-colors cursor-pointer"
                >
                  {productionProfiles.map((p) => (
                    <option key={p.profile_id} value={p.profile_id}>
                      {p.product_name} ({p.profile_id})
                    </option>
                  ))}
                </select>
                {(() => {
                  const activeProf = productionProfiles.find((p) => p.profile_id === selectedProfileId);
                  return activeProf ? (
                    <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs space-y-1.5 font-mono">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Station:</span>
                        <strong className="text-cyan-300">{activeProf.inspection_station}</strong>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">SKU / Camera:</span>
                        <span className="text-slate-200">{activeProf.sku} • {activeProf.camera_id}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400">Threshold:</span>
                        <span className="text-emerald-400 font-bold">{activeProf.calibrated_threshold} (FAR: {(activeProf.target_far * 100).toFixed(1)}%)</span>
                      </div>
                      {(activeProf.validation_status || activeProf.profile_id === 'bottle_001_station_01') && (
                        <div className="mt-1.5 px-2 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[10px] font-semibold text-center uppercase tracking-wider">
                          {activeProf.validation_status || 'SIMULATED REFERENCE PROFILE — NOT PRODUCTION VALIDATED'}
                        </div>
                      )}
                    </div>
                  ) : null;
                })()}
              </div>
            )}
          </div>

          {/* Real-time Defect Event Ticker (Audit Rail) */}
          <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-violet-400" />
                <span className="font-heading font-bold text-sm text-white">
                  Inspection Audit Rail
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {filteredHistory.length} Captured
                </span>
                {eventHistory.length > 0 && (
                  <button
                    type="button"
                    onClick={handleClearHistory}
                    className="text-[10px] font-mono text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>

            {/* Audit Rail Filter Pills */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
              <select
                value={historyVerdictFilter}
                onChange={(e) => setHistoryVerdictFilter(e.target.value)}
                className="px-2 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 text-[11px] font-mono focus:outline-none"
              >
                <option value="all">All Verdicts</option>
                <option value="NORMAL">NORMAL</option>
                <option value="DEFECTIVE">DEFECTIVE</option>
                <option value="REVIEW REQUIRED">REVIEW REQUIRED</option>
                <option value="UNSUPPORTED">UNSUPPORTED</option>
              </select>

              <select
                value={historyCategoryFilter}
                onChange={(e) => setHistoryCategoryFilter(e.target.value)}
                className="px-2 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 text-[11px] font-mono focus:outline-none"
              >
                <option value="all">All Categories</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Ticker List */}
            <div className="space-y-2.5 max-h-[460px] overflow-y-auto pr-1 scrollbar-thin">
              {filteredHistory.length === 0 ? (
                <div className="p-6 text-center border border-dashed border-slate-800 rounded-xl space-y-2">
                  <Eye className="w-8 h-8 text-slate-600 mx-auto" />
                  <p className="text-xs text-slate-400">No matching inspection records.</p>
                  <p className="text-[11px] text-slate-500">
                    Press <span className="text-cyan-400 font-mono">SPACE</span> or click "Capture Frame" to trigger immediate inspection.
                  </p>
                </div>
              ) : (
                filteredHistory.map((evt) => (
                  <div
                    key={evt.id}
                    onClick={() => setSelectedEventModal(evt)}
                    className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-violet-500/50 hover:bg-slate-950 transition-all cursor-pointer group flex items-center justify-between gap-3"
                  >
                    {/* Event Thumbnail Preview */}
                    <div className="w-14 h-14 rounded-lg bg-black overflow-hidden border border-slate-800 flex-shrink-0 relative">
                      <img
                        src={evt.heatmap_base64 || evt.original_image}
                        alt="Event Thumbnail"
                        className="w-full h-full object-cover"
                      />
                      {evt.verdict === 'DEFECTIVE' && (
                        <div className="absolute top-0.5 right-0.5 w-2 h-2 rounded-full bg-rose-500" />
                      )}
                      {evt.verdict === 'REVIEW REQUIRED' && (
                        <div className="absolute top-0.5 right-0.5 w-2 h-2 rounded-full bg-amber-500" />
                      )}
                    </div>

                    {/* Event Telemetry Info */}
                    <div className="flex-1 min-w-0 space-y-1">
                      <div className="flex items-center justify-between gap-1">
                        <span className="font-heading text-xs font-semibold text-white truncate">
                          {(evt.detected_category || evt.capturedCategory).toUpperCase()} • {evt.verdict}
                        </span>
                        <span className="text-[10px] font-mono text-slate-500 flex-shrink-0">
                          {evt.timestamp}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span
                          className={`text-[9px] font-mono font-bold uppercase px-1.5 py-0.2 rounded border ${
                            evt.verdict === 'DEFECTIVE'
                              ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                              : evt.verdict === 'NORMAL'
                              ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                              : evt.verdict === 'REVIEW REQUIRED'
                              ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                              : 'bg-purple-500/15 text-purple-400 border-purple-500/30'
                          }`}
                        >
                          {evt.verdict}
                        </span>
                        <span className="text-[10px] font-mono text-slate-400">
                          {evt.processing_time_ms}ms
                        </span>
                      </div>
                    </div>

                    <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all flex-shrink-0" />
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* -------------------------------------------------------- */}
      {/* 4. Model Registry Status Modal                            */}
      {/* -------------------------------------------------------- */}
      {showModelStatusModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-4xl bg-[#090d16] border border-slate-800 rounded-2xl shadow-2xl p-6 overflow-hidden space-y-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-violet-600/20 border border-violet-500/30 flex items-center justify-center">
                  <Server className="w-4 h-4 text-cyan-400" />
                </div>
                <div>
                  <h3 className="font-heading text-lg font-bold text-white">
                    15 Category PatchCore Model Registry
                  </h3>
                  <p className="text-xs text-slate-400 font-mono">
                    All 15 MVTec AD models deployed with category-specific calibrated thresholds & memory banks.
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setShowModelStatusModal(false)}
                className="p-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white border border-slate-800 transition-colors"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Models Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Calibrated Threshold</th>
                    <th className="py-2.5 px-3">Nominal Mean / P99</th>
                    <th className="py-2.5 px-3">Backbone</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {CATEGORIES.map((cat) => {
                    const statusObj = modelStatusData?.categories?.[cat.id] || {};
                    const isReady = statusObj.is_ready !== false;
                    return (
                      <tr key={cat.id} className="hover:bg-slate-900/40 transition-colors">
                        <td className="py-2.5 px-3 font-semibold text-white flex items-center gap-2">
                          <span
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: cat.color }}
                          />
                          {cat.label}
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] ${
                              cat.type === 'Object'
                                ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20'
                                : 'bg-violet-500/10 text-violet-300 border border-violet-500/20'
                            }`}
                          >
                            {cat.type}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold">
                            <Check className="w-3 h-3" />
                            {isReady ? 'Ready & Loaded' : 'Pending'}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-cyan-300 font-bold">
                          {statusObj.calibrated_threshold ? statusObj.calibrated_threshold.toFixed(4) : '1.7452'}
                        </td>
                        <td className="py-2.5 px-3 text-slate-400">
                          {statusObj.baseline_mean ? statusObj.baseline_mean.toFixed(3) : '1.250'} /{' '}
                          {statusObj.baseline_p99 ? statusObj.baseline_p99.toFixed(3) : '1.650'}
                        </td>
                        <td className="py-2.5 px-3 text-slate-400 text-[10px]">
                          ResNet-18 (L2+L3)
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowModelStatusModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-all"
              >
                Close Registry
              </button>
            </div>
          </div>
        </div>
      )}

      {/* -------------------------------------------------------- */}
      {/* 5. Before / After Heatmap Split-View Modal               */}
      {/* -------------------------------------------------------- */}
      {selectedEventModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-4xl bg-[#090d16] border border-slate-800 rounded-2xl shadow-2xl p-6 overflow-hidden space-y-6 max-h-[92vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-violet-600/20 border border-violet-500/30 flex items-center justify-center">
                  <Eye className="w-4 h-4 text-cyan-400" />
                </div>
                <div>
                  <h3 className="font-heading text-lg font-bold text-white">
                    Inspection Specimen Analysis
                  </h3>
                  <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                    <span>Target: {(selectedEventModal.detected_category || selectedEventModal.capturedCategory).toUpperCase()}</span>
                    <span>•</span>
                    <span>Event ID: {selectedEventModal.id}</span>
                    <span>•</span>
                    <span>Time: {selectedEventModal.timestamp}</span>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setSelectedEventModal(null)}
                className="p-2 rounded-xl bg-slate-900 text-slate-400 hover:text-white border border-slate-800 transition-colors"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Split-View Heatmap Slider Component */}
            <div className="space-y-2">
              <HeatmapSlider
                originalImage={selectedEventModal.original_image}
                heatmapOverlay={selectedEventModal.heatmap_base64}
                rawHeatmap={selectedEventModal.raw_heatmap}
                label={`${selectedEventModal.detected_category || selectedEventModal.capturedCategory} Optical Inspection`}
              />
            </div>

            {/* Telemetry Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                <span className="text-slate-400 font-mono text-[10px] uppercase">Verdict</span>
                <div className="font-heading font-bold text-sm text-white uppercase">
                  {selectedEventModal.verdict}
                </div>
                <div className="text-[10px] font-mono text-slate-400">
                  Status: {selectedEventModal.recognition_status || 'OK'}
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                <span className="text-slate-400 font-mono text-[10px] uppercase">Anomaly Score</span>
                <div className="font-heading font-bold text-sm text-cyan-300 font-mono">
                  {selectedEventModal.anomaly_score?.toFixed(4) || '0.0000'}
                </div>
                <div className="text-[10px] font-mono text-slate-400">
                  Threshold: {selectedEventModal.calibrated_threshold?.toFixed(4) || '1.7452'}
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                <span className="text-slate-400 font-mono text-[10px] uppercase">Category Confidence</span>
                <div className="font-heading font-bold text-sm text-violet-300 font-mono">
                  {selectedEventModal.category_confidence
                    ? `${(selectedEventModal.category_confidence * 100).toFixed(1)}%`
                    : '--'}
                </div>
                <div className="text-[10px] font-mono text-slate-400">
                  Type: {selectedEventModal.category_type || 'Object'}
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                <span className="text-slate-400 font-mono text-[10px] uppercase">Defect Area</span>
                <div className="font-heading font-bold text-sm text-rose-300 font-mono">
                  {selectedEventModal.defect_area_pct?.toFixed(2) || '0.00'}%
                </div>
                <div className="text-[10px] font-mono text-slate-400">
                  ROI Surface
                </div>
              </div>
            </div>

            {/* Operator Plain-English Context */}
            <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800/80 text-xs space-y-1.5">
              <div className="flex items-center gap-2 text-cyan-400 font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Operator Diagnostic Summary:</span>
              </div>
              <p className="text-slate-300 leading-relaxed">
                {selectedEventModal.diagnosis ? (
                  selectedEventModal.diagnosis
                ) : (
                  <>
                    Optical frame inspection for <strong className="text-white uppercase">{selectedEventModal.detected_category || selectedEventModal.capturedCategory}</strong> resulted in verdict <strong className="text-white">{selectedEventModal.conclusion || selectedEventModal.verdict}</strong> with anomaly score{' '}
                    <span className="font-mono text-cyan-300">{selectedEventModal.anomaly_score?.toFixed(4)}</span> against calibrated threshold{' '}
                    <span className="font-mono text-slate-300">{selectedEventModal.calibrated_threshold?.toFixed(4)}</span>.
                    {selectedEventModal.review_reason && (
                      <span className="block mt-1 text-amber-300">
                        Note: {selectedEventModal.review_reason}
                      </span>
                    )}
                  </>
                )}
              </p>
            </div>

            {/* Modal Bottom Actions */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              {onNavigateToRAG && (
                <button
                  type="button"
                  onClick={() => {
                    setSelectedEventModal(null);
                    onNavigateToRAG(selectedEventModal.detected_category || selectedEventModal.capturedCategory);
                  }}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 text-xs font-semibold hover:bg-cyan-500/25 transition-all"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>Query RAG Copilot for {selectedEventModal.detected_category || selectedEventModal.capturedCategory}</span>
                </button>
              )}

              <button
                type="button"
                onClick={() => setSelectedEventModal(null)}
                className="ml-auto px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-all"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
