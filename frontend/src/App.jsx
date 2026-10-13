import React, { useState, useEffect } from 'react';
import SidebarNav from './components/ui/SidebarNav';
import HeroSection from './components/sections/HeroSection';
import InspectSection from './components/sections/InspectSection';
import ModelComparisonSection from './components/sections/ModelComparisonSection';
import HistoryBrowserSection from './components/sections/HistoryBrowserSection';
import BatchInspectionSection from './components/sections/BatchInspectionSection';
import KnowledgeBaseRAGSection from './components/sections/KnowledgeBaseRAGSection';
import ConversationalDashboardSection from './components/sections/ConversationalDashboardSection';
import SimilarityExplorerSection from './components/sections/SimilarityExplorerSection';
import DriftMonitorSection from './components/sections/DriftMonitorSection';
import ActiveLearningRCASection from './components/sections/ActiveLearningRCASection';
import LiveStreamInspector from './pages/LiveStreamInspector';
import { api } from './api/client';
import { ShieldAlert, Info, Cpu, ExternalLink } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('inspect');
  const [backendHealth, setBackendHealth] = useState(null);
  const [similarityCategory, setSimilarityCategory] = useState('bottle');
  const [ragInitialQuery, setRagInitialQuery] = useState('');

  // Check backend health periodically
  useEffect(() => {
    async function checkServer() {
      try {
        const health = await api.checkHealth();
        setBackendHealth(health);
      } catch (err) {
        console.warn('Backend server check failed:', err);
        setBackendHealth({ status: 'offline' });
      }
    }

    checkServer();
    const timer = setInterval(checkServer, 10000);
    return () => clearInterval(timer);
  }, []);

  // Contextual transitions from Inspect flow
  const handleNavigateToSimilarity = (category) => {
    setSimilarityCategory(category || 'bottle');
    setActiveTab('similarity');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigateToRAG = (defectType) => {
    setRagInitialQuery(
      defectType ? `Explain the root cause, process impact, and prevention of ${defectType}` : ''
    );
    setActiveTab('rag');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 selection:bg-violet-600 selection:text-white flex">
      {/* Left Sidebar Navigation */}
      <SidebarNav
        activeTab={activeTab}
        onTabChange={(tab) => {
          setActiveTab(tab);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        backendHealth={backendHealth}
      />

      {/* Main Content Area offset by Sidebar on desktop */}
      <div className="flex-1 flex flex-col md:pl-64 min-w-0">
        <main className="flex-1">
        {activeTab === 'inspect' && (
          <>
            <HeroSection
              onStartInspect={() => {
                const el = document.getElementById('inspect-workspace');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
              onViewModelComparison={() => {
                setActiveTab('models');
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
            />
            <div id="inspect-workspace">
              <InspectSection
                onNavigateToSimilarity={handleNavigateToSimilarity}
                onNavigateToRAG={handleNavigateToRAG}
              />
            </div>
          </>
        )}

        {activeTab === 'live' && (
          <LiveStreamInspector
            onNavigateToRAG={handleNavigateToRAG}
            onNavigateToSimilarity={handleNavigateToSimilarity}
          />
        )}

        {activeTab === 'models' && <ModelComparisonSection />}

        {activeTab === 'history' && <HistoryBrowserSection />}

        {activeTab === 'batch' && <BatchInspectionSection />}

        {activeTab === 'rag' && <KnowledgeBaseRAGSection initialQuery={ragInitialQuery} />}

        {activeTab === 'dashboard' && <ConversationalDashboardSection />}

        {activeTab === 'similarity' && (
          <SimilarityExplorerSection initialCategory={similarityCategory} />
        )}

        {activeTab === 'drift' && <DriftMonitorSection />}

        {activeTab === 'rca' && <ActiveLearningRCASection />}
      </main>

      {/* Production Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/90 py-12 px-4 sm:px-6 lg:px-8 mt-16 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex flex-col gap-1.5 text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-2">
              <span className="font-heading font-bold text-sm text-white">DefectVision AI</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Production-Ready
              </span>
            </div>
            <p className="text-slate-400 max-w-md text-[11px]">
              Combining PatchCore anomaly coreset banks, EfficientNet-B0 v3 leak-free classification, and local LLM explanations over the 15 MVTec AD industrial categories.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 font-mono text-[11px]">
            <button
              type="button"
              onClick={() => setActiveTab('models')}
              className="hover:text-cyan-300 transition-colors"
            >
              AUROC Leaderboard
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('history')}
              className="hover:text-cyan-300 transition-colors"
            >
              1,725 Benchmark Logs
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('rag')}
              className="hover:text-cyan-300 transition-colors"
            >
              16 Defect Taxonomies
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('drift')}
              className="hover:text-cyan-300 transition-colors"
            >
              Production Drift
            </button>
          </div>

          <div className="text-[11px] font-mono text-slate-400 text-center md:text-right space-y-1">
            <div>
              Live URL:{' '}
              <a
                href="https://defectvision-ai.vercel.app/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-cyan-400 hover:text-cyan-300 font-semibold underline underline-offset-2"
              >
                defectvision-ai.vercel.app ↗
              </a>
            </div>
            <div>
              GitHub:{' '}
              <a
                href="https://github.com/suryacharan945/DefectVision-AI"
                target="_blank"
                rel="noopener noreferrer"
                className="text-violet-400 hover:text-violet-300 hover:underline"
              >
                suryacharan945/DefectVision-AI ↗
              </a>
            </div>
          </div>
        </div>
      </footer>
      </div>
    </div>
  );
}
