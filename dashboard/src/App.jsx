import React, { useState, useEffect, useMemo, useRef } from 'react';
import './App.css';
import { MOCK_PROJECT, MOCK_SUMMARY, MOCK_ELEMENTS } from './mockData';

export const isMobileDevice = () => {
  if (typeof window === 'undefined') return false;
  const ua = navigator.userAgent || '';
  const isCapacitor = Boolean(window.Capacitor);
  const isMobileUa = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
  const isTouchScreen = ('ontouchstart' in window || navigator.maxTouchPoints > 0) && window.innerWidth <= 820;
  return isCapacitor || isMobileUa || isTouchScreen;
};

export const CANDIDATE_BACKENDS = [
  'https://lucky-rings-strive.loca.lt/api',
  'http://192.168.29.102:8000/api',
  'http://localhost:8000/api'
];

export const getDefaultApiBase = () => {
  if (typeof window !== 'undefined') {
    const origin = window.location.origin;

    // 1. If currently loaded from ANY remote web address (localtunnel, Render, LAN IP),
    // ALWAYS use the origin we are loaded from! Both frontend and backend run on that same host!
    if (origin && !origin.includes('localhost') && !origin.includes('127.0.0.1') && !origin.startsWith('capacitor:') && !origin.startsWith('ionic:') && !origin.startsWith('file:') && !origin.includes('null')) {
      return `${origin}/api`;
    }

    // 2. Check if the user manually saved a custom URL in settings (purge stale 503 URLs)
    const saved = localStorage.getItem('buildlens_backend_url');
    if (saved && saved.trim()) {
      const clean = saved.trim().replace(/\/+$/, '');
      if (clean.includes('trycloudflare.com') || clean.includes('buildlens4d.loca.lt') || (isMobileDevice() && (clean.includes('localhost') || clean.includes('127.0.0.1')))) {
        localStorage.removeItem('buildlens_backend_url');
      } else {
        return clean;
      }
    }

    // 3. If running inside Capacitor mobile app or file scheme:
    if (isMobileDevice()) {
      return 'https://lucky-rings-strive.loca.lt/api';
    }

    // 4. Desktop development
    if (window.location.port === '5173') {
      return 'http://localhost:8000/api';
    }
    return `${origin}/api`;
  }
  return 'https://lucky-rings-strive.loca.lt/api';
};

export const apiFetch = async (endpoint, options = {}, customBase = null, timeoutMs = 12000) => {
  const base = (customBase || getDefaultApiBase()).replace(/\/+$/, '');
  const url = endpoint.startsWith('http') ? endpoint : `${base}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const existingHeaders = options.headers || {};
  const isFormData = options.body instanceof FormData;

  const headers = {
    'Bypass-Tunnel-Reminder': '1',
    'bypass-tunnel-reminder': '1',
    ...existingHeaders
  };

  if (!isFormData && !headers['Content-Type'] && options.body && typeof options.body === 'string') {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal
    });
    return res;
  } finally {
    clearTimeout(timer);
  }
};

export default function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState(getDefaultApiBase);
  const [serverLatency, setServerLatency] = useState(null);
  const [serverHealth, setServerHealth] = useState(null);
  const [showServerConfigModal, setShowServerConfigModal] = useState(false);
  const [serverConfigInput, setServerConfigInput] = useState(getDefaultApiBase);
  const [testingConnection, setTestingConnection] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'scrubber', 'review_queue', 'cv_scanner', 'markers', 'audit_trail', 'reports'
  const [mode, setMode] = useState('live'); // 'live' or 'mock'
  const [isApiOnline, setIsApiOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const [project, setProject] = useState(MOCK_PROJECT);
  const [summary, setSummary] = useState(MOCK_SUMMARY);
  const [elements, setElements] = useState(MOCK_ELEMENTS);
  const [reviewDecisions, setReviewDecisions] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [governanceData, setGovernanceData] = useState(null);
  const [benchmarks, setBenchmarks] = useState([]);

  // Spatial Zone & Floor Isolator Filter
  const [selectedFilter, setSelectedFilter] = useState('ALL');
  const [selectedZone, setSelectedZone] = useState('ALL');
  const [selectedFloor, setSelectedFloor] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [inspectElement, setInspectElement] = useState(null);

  // Evidence Photos State
  const [elementEvidences, setElementEvidences] = useState([]);
  const [evidenceLoading, setEvidenceLoading] = useState(false);
  const [uploadNotes, setUploadNotes] = useState('On-site photographic evidence');
  const [uploadObserver, setUploadObserver] = useState('eng_field_01');
  const [uploadingEvidence, setUploadingEvidence] = useState(false);
  const fileInputRef = useRef(null);

  // 4D Time Scrubber State
  const [scrubberDate, setScrubberDate] = useState('2026-10-11');
  const [isPlayingScrubber, setIsPlayingScrubber] = useState(false);
  const [simulationData, setSimulationData] = useState(null);
  const scrubberTimerRef = useRef(null);

  // Review Queue State
  const [selectedReviewElement, setSelectedReviewElement] = useState(null);
  const [reviewerId, setReviewerId] = useState('coord_elena_01');
  const [reviewDecisionType, setReviewDecisionType] = useState('confirmed');
  const [reviewReason, setReviewReason] = useState('Verified field engineering photos; obstruction cleared and installation conforms to IFC specification.');
  const [reviewSubmitting, setReviewSubmitting] = useState(false);

  // CV Assistance State (FR-026, FR-027, SRS 8.3)
  const [cvTargetElementId, setCvTargetElementId] = useState('BM-L1-02');
  const [cvConfidence, setCvConfidence] = useState(0.55);
  const [cvOccluded, setCvOccluded] = useState(true);
  const [cvResult, setCvResult] = useState(null);
  const [cvAnalyzing, setCvAnalyzing] = useState(false);

  // Benchmark Target State
  const [selectedBenchmark, setSelectedBenchmark] = useState(null);

  // Building Plan & Image Verification State (FR-026, FR-027, FR-030)
  const [verificationFile, setVerificationFile] = useState(null);
  const [verificationPreviewUrl, setVerificationPreviewUrl] = useState(null);
  const [verificationPlanType, setVerificationPlanType] = useState('site_photo');
  const [verificationZone, setVerificationZone] = useState('ALL');
  const [verificationObserver, setVerificationObserver] = useState('eng_field_01');
  const [verificationLoading, setVerificationLoading] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [verificationHistory, setVerificationHistory] = useState([]);
  const verificationInputRef = useRef(null);

  // PWA Mobile App Installation State
  const [deferredInstallPrompt, setDeferredInstallPrompt] = useState(null);
  const [isAppInstalled, setIsAppInstalled] = useState(false);
  const [showInstallGuide, setShowInstallGuide] = useState(false);

  useEffect(() => {
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredInstallPrompt(e);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    window.addEventListener('appinstalled', () => {
      setIsAppInstalled(true);
      setDeferredInstallPrompt(null);
    });

    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsAppInstalled(true);
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
    };
  }, []);

  const handleInstallClick = async () => {
    if (deferredInstallPrompt) {
      deferredInstallPrompt.prompt();
      const { outcome } = await deferredInstallPrompt.userChoice;
      if (outcome === 'accepted') {
        setIsAppInstalled(true);
      }
      setDeferredInstallPrompt(null);
    } else {
      setShowInstallGuide(true);
    }
  };


  // File selection for Plan & Image Verification
  const handleSelectVerificationFile = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setVerificationFile(file);
      setVerificationPreviewUrl(URL.createObjectURL(file));
      setVerificationResult(null);
    }
  };

  // Submit Plan/Image for 4D Verification
  const handleRunImageVerification = async (e) => {
    e?.preventDefault();
    if (!verificationFile) {
      alert("Please select a building photo or plan image to verify.");
      return;
    }
    setVerificationLoading(true);
    setErrorMsg(null);

    try {
      const formData = new FormData();
      formData.append('file', verificationFile);
      formData.append('plan_type', verificationPlanType);
      formData.append('target_zone', verificationZone);
      formData.append('observer_id', verificationObserver);

      const projId = 'proj-terminal-04';
      const res = await apiFetch(`/projects/${projId}/verify-image`, {
        method: 'POST',
        body: formData
      }, apiBaseUrl, 30000);

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Image verification failed.');
      }

      const result = await res.json();
      setVerificationResult(result);
      loadData(mode);
      loadVerificationHistory();
    } catch (err) {
      console.error("Verification error:", err);
      setErrorMsg(`Verification failed: ${err.message}`);
    } finally {
      setVerificationLoading(false);
    }
  };

  const loadVerificationHistory = async () => {
    try {
      const projId = 'proj-terminal-04';
      const res = await apiFetch(`/projects/${projId}/verification-reports`, {}, apiBaseUrl);
      if (res.ok) {
        setVerificationHistory(await res.json());
      }
    } catch (e) {
      console.warn("Could not load verification history:", e);
    }
  };

  const handleTestAndApplyServer = async (testUrl = serverConfigInput) => {
    setTestingConnection(true);
    setTestResult(null);
    const cleanUrl = testUrl.trim().replace(/\/+$/, '');
    try {
      const startTime = performance.now();
      const res = await apiFetch('/health', {}, cleanUrl, 8000);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      const data = await res.json();
      const latency = Math.round(performance.now() - startTime);

      localStorage.setItem('buildlens_backend_url', cleanUrl);
      setApiBaseUrl(cleanUrl);
      setServerConfigInput(cleanUrl);
      setServerLatency(latency);
      setServerHealth(data);
      setIsApiOnline(true);
      setErrorMsg(null);
      setTestResult({ success: true, message: `Connected! Latency: ${latency}ms | DB: ${data.database || 'connected'}` });
      await loadData('live', cleanUrl);
    } catch (err) {
      setTestResult({
        success: false,
        message: `Connection failed: ${err.name === 'AbortError' ? 'Connection timed out (8s)' : err.message}`
      });
    } finally {
      setTestingConnection(false);
    }
  };

  // Load all initial project data with Auto-Discovery & Resilient Fallback
  const loadData = async (targetMode = mode, targetApiBase = null) => {
    setLoading(true);
    setErrorMsg(null);

    if (targetMode === 'mock') {
      setProject(MOCK_PROJECT);
      setSummary(MOCK_SUMMARY);
      setElements(MOCK_ELEMENTS);
      setIsApiOnline(false);
      setLoading(false);
      return;
    }

    let base = targetApiBase || apiBaseUrl;

    // If currently loaded from a real domain or LAN IP, ALWAYS use current origin/api!
    if (typeof window !== 'undefined' && window.location.origin && !window.location.origin.includes('localhost') && !window.location.origin.includes('127.0.0.1') && !window.location.origin.startsWith('capacitor:') && !window.location.origin.startsWith('file:') && !window.location.origin.includes('null')) {
      base = `${window.location.origin}/api`;
    }

    // Purge dead 503 URLs or invalid localhost on mobile
    if (base.includes('trycloudflare.com') || base.includes('buildlens4d.loca.lt') || (isMobileDevice() && (base.includes('localhost') || base.includes('127.0.0.1')))) {
      base = (typeof window !== 'undefined' && window.location.origin && !window.location.origin.includes('localhost') && !window.location.origin.includes('127.0.0.1') && !window.location.origin.startsWith('capacitor:'))
        ? `${window.location.origin}/api`
        : 'https://lucky-rings-strive.loca.lt/api';
      setApiBaseUrl(base);
      localStorage.setItem('buildlens_backend_url', base);
    }

    let activeBase = null;
    let healthData = null;
    let latencyMs = 0;

    // 1. Test current primary target base
    try {
      const startTime = performance.now();
      const res = await apiFetch('/health', {}, base, 4000);
      if (res.ok) {
        healthData = await res.json();
        latencyMs = Math.round(performance.now() - startTime);
        activeBase = base;
      }
    } catch (e) {
      console.warn(`Primary backend ${base} unreachable (${e.message}), initiating auto-discovery...`);
    }

    // 2. If primary target failed, probe candidate backends automatically!
    if (!activeBase) {
      const candidatesToProbe = [
        (typeof window !== 'undefined' && window.location.origin ? `${window.location.origin}/api` : null),
        'https://lucky-rings-strive.loca.lt/api',
        'http://192.168.29.102:8000/api',
        'http://localhost:8000/api'
      ].filter(Boolean);

      for (const candidate of candidatesToProbe) {
        if (candidate === base) continue;
        try {
          const startTime = performance.now();
          const res = await apiFetch('/health', {}, candidate, 3500);
          if (res.ok) {
            healthData = await res.json();
            latencyMs = Math.round(performance.now() - startTime);
            activeBase = candidate;
            console.log(`Auto-discovery succeeded! Connected to ${candidate}`);
            setApiBaseUrl(candidate);
            setServerConfigInput(candidate);
            localStorage.setItem('buildlens_backend_url', candidate);
            break;
          }
        } catch (err) {
          // Probe next candidate
        }
      }
    }

    if (!activeBase) {
      console.warn('All candidate backends unreachable, falling back to mock demo mode.');
      setIsApiOnline(false);
      setErrorMsg(`Could not connect to FastAPI backend at ${base}. Demonstrator Mock Mode active. Tap ⚙️ in header to select server.`);
      setProject(MOCK_PROJECT);
      setSummary(MOCK_SUMMARY);
      setElements(MOCK_ELEMENTS);
      setLoading(false);
      return;
    }

    // 3. Backend is confirmed online! Fetch project datasets
    try {
      setServerLatency(latencyMs);
      setServerHealth(healthData);
      setIsApiOnline(true);
      setErrorMsg(null);

      const projId = 'proj-terminal-04';
      const [projRes, sumRes, elemRes, revRes, audRes, repRes, markRes, verRes] = await Promise.all([
        apiFetch(`/projects/${projId}`, {}, activeBase),
        apiFetch(`/projects/${projId}/summary`, {}, activeBase),
        apiFetch(`/projects/${projId}/elements`, {}, activeBase),
        apiFetch(`/projects/${projId}/reviews`, {}, activeBase),
        apiFetch(`/projects/${projId}/audit-trail`, {}, activeBase),
        apiFetch(`/projects/${projId}/report/summary`, {}, activeBase),
        apiFetch(`/projects/${projId}/markers`, {}, activeBase),
        apiFetch(`/projects/${projId}/verification-reports`, {}, activeBase)
      ]);

      if (projRes.ok) setProject(await projRes.json());
      if (sumRes.ok) setSummary(await sumRes.json());
      if (elemRes.ok) setElements(await elemRes.json());
      if (revRes.ok) setReviewDecisions(await revRes.json());
      if (audRes.ok) setAuditLogs(await audRes.json());
      if (repRes.ok) setGovernanceData(await repRes.json());
      if (verRes && verRes.ok) setVerificationHistory(await verRes.json());
      if (markRes.ok) {
        const bmList = await markRes.json();
        setBenchmarks(bmList);
        if (bmList.length > 0 && !selectedBenchmark) setSelectedBenchmark(bmList[0]);
      }
    } catch (err) {
      console.warn('Backend dataset fetch error:', err);
      setIsApiOnline(false);
      setErrorMsg(`Connected to ${activeBase} but failed to load datasets: ${err.message}`);
      setProject(MOCK_PROJECT);
      setSummary(MOCK_SUMMARY);
      setElements(MOCK_ELEMENTS);
    } finally {
      setLoading(false);
    }
  };

  // Fetch 4D Simulation Snapshot for Scrubber Date
  const fetchSimulation = async (dateStr) => {
    try {
      const projId = 'proj-terminal-04';
      const res = await apiFetch(`/projects/${projId}/simulation?target_date=${dateStr}`, {}, apiBaseUrl);
      if (res.ok) {
        setSimulationData(await res.json());
      }
    } catch (e) {
      console.warn("Simulation fetch error:", e);
    }
  };

  useEffect(() => {
    fetchSimulation(scrubberDate);
  }, [scrubberDate]);

  // Scrubber Auto-Playback Loop
  useEffect(() => {
    if (isPlayingScrubber) {
      scrubberTimerRef.current = setInterval(() => {
        setScrubberDate((prev) => {
          const d = new Date(prev);
          d.setDate(d.getDate() + 1);
          if (d > new Date('2026-11-15')) {
            setIsPlayingScrubber(false);
            return '2026-08-15';
          }
          return d.toISOString().split('T')[0];
        });
      }, 500);
    } else {
      if (scrubberTimerRef.current) clearInterval(scrubberTimerRef.current);
    }
    return () => {
      if (scrubberTimerRef.current) clearInterval(scrubberTimerRef.current);
    };
  }, [isPlayingScrubber]);

  // Fetch Evidence for Modal
  const loadElementEvidences = async (elemId) => {
    setEvidenceLoading(true);
    try {
      const projId = 'proj-terminal-04';
      const res = await apiFetch(`/projects/${projId}/elements/${elemId}/evidence`, {}, apiBaseUrl);
      if (res.ok) {
        setElementEvidences(await res.json());
      } else {
        setElementEvidences([]);
      }
    } catch (e) {
      setElementEvidences([]);
    } finally {
      setEvidenceLoading(false);
    }
  };

  const handleOpenInspect = (el) => {
    setInspectElement(el);
    loadElementEvidences(el.id);
  };

  // Upload Evidence Photo
  const handleUploadEvidence = async (e) => {
    e.preventDefault();
    if (!fileInputRef.current || !fileInputRef.current.files[0]) {
      alert("Please select an image file to upload.");
      return;
    }
    const file = fileInputRef.current.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('observer_id', uploadObserver);
    formData.append('reported_state', inspectElement.verification_state || 'in_progress');
    formData.append('notes', uploadNotes);
    formData.append('camera_pose_json', JSON.stringify({ pos: [1.2, 1.5, -4.2], rot: [0, 0, 0, 1] }));

    setUploadingEvidence(true);
    try {
      const projId = 'proj-terminal-04';
      const res = await apiFetch(`/projects/${projId}/elements/${inspectElement.id}/evidence`, {
        method: 'POST',
        body: formData
      }, apiBaseUrl, 25000);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }
      alert("Inspection evidence photo uploaded successfully!");
      if (fileInputRef.current) fileInputRef.current.value = '';
      await loadElementEvidences(inspectElement.id);
      await loadData('live');
    } catch (err) {
      alert(`Error uploading evidence: ${err.message}`);
    } finally {
      setUploadingEvidence(false);
    }
  };

  // Update Observation
  const handleUpdateObservation = async (elementId, reportedState, notes) => {
    try {
      const projId = 'proj-terminal-04';
      const res = await apiFetch(`/projects/${projId}/observations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          element_id: elementId,
          observer_id: 'web_dashboard_inspector',
          reported_state: reportedState,
          confidence_score: reportedState === 'occluded' ? 0.45 : 0.95,
          notes: notes || `Field observation updated from Web Dashboard (${reportedState})`
        })
      }, apiBaseUrl);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to submit observation');
      }
      await loadData('live');
      setInspectElement(null);
    } catch (err) {
      alert(`Error submitting observation: ${err.message}`);
    }
  };

  // Submit Human Review Decision (FR-022, FR-024)
  const handleSubmitReviewDecision = async (e) => {
    e.preventDefault();
    if (!selectedReviewElement) {
      alert("Please select a BIM element from the review queue first.");
      return;
    }
    setReviewSubmitting(true);
    try {
      const projId = 'proj-terminal-04';
      const res = await apiFetch(`/projects/${projId}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          element_id: selectedReviewElement.id,
          reviewer_id: reviewerId,
          decision: reviewDecisionType,
          reason: reviewReason
        })
      }, apiBaseUrl);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to submit review decision');
      }
      await loadData('live');
      alert(`Review decision recorded! Element ${selectedReviewElement.id} status updated. Unity 3D model will reflect change immediately.`);
      setSelectedReviewElement(null);
    } catch (err) {
      alert(`Error submitting review decision: ${err.message}`);
    } finally {
      setReviewSubmitting(false);
    }
  };

  // Run CV Detection Proposal (FR-026, FR-027, SRS 8.3)
  const handleRunCVAnalysis = async () => {
    setCvAnalyzing(true);
    try {
      const projId = 'proj-terminal-04';
      const res = await apiFetch(`/projects/${projId}/cv-detect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          simulated_element_id: cvTargetElementId,
          simulated_confidence: parseFloat(cvConfidence),
          simulated_occlusion: cvOccluded
        })
      }, apiBaseUrl);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to analyze element');
      }
      const data = await res.json();
      setCvResult(data);
    } catch (err) {
      alert(`Error executing CV detector: ${err.message}`);
    } finally {
      setCvAnalyzing(false);
    }
  };

  useEffect(() => {
    loadData(mode);
  }, [mode]);

  // Review Queue Items
  const reviewQueueElements = useMemo(() => {
    return elements.filter(el => el.verification_state === 'needs_manual_review' || el.verification_state === 'potentially_delayed');
  }, [elements]);

  // Unique Spatial Zones
  const uniqueZones = useMemo(() => {
    const s = new Set();
    elements.forEach(el => { if (el.spatial_zone) s.add(el.spatial_zone); });
    return Array.from(s);
  }, [elements]);

  // Filter Elements for Overview
  const filteredElements = useMemo(() => {
    return elements.filter(el => {
      const matchesState = selectedFilter === 'ALL' || el.verification_state === selectedFilter;
      const matchesZone = selectedZone === 'ALL' || el.spatial_zone === selectedZone;
      let matchesFloor = true;
      if (selectedFloor === 'Foundation') matchesFloor = el.element_type === 'Footing' || el.element_type === 'Wall';
      else if (selectedFloor === 'Ground') matchesFloor = (el.spatial_zone || '').includes('Ground') || el.element_type === 'Column';
      else if (selectedFloor === 'Mezzanine') matchesFloor = (el.spatial_zone || '').includes('Mezzanine') || (el.spatial_zone || '').includes('Ticket Hall');
      
      const matchesSearch = searchQuery === '' ||
        el.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        el.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        el.element_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (el.spatial_zone && el.spatial_zone.toLowerCase().includes(searchQuery.toLowerCase()));

      return matchesState && matchesZone && matchesFloor && matchesSearch;
    });
  }, [elements, selectedFilter, selectedZone, selectedFloor, searchQuery]);

  const stateColors = {
    verified_complete: { bg: '#059669', badge: 'badge-complete', label: 'Verified Complete', icon: '✓' },
    in_progress: { bg: '#d97706', badge: 'badge-progress', label: 'In Progress', icon: '⏳' },
    potentially_delayed: { bg: '#dc2626', badge: 'badge-delayed', label: 'Delayed', icon: '⚠' },
    ahead_of_schedule: { bg: '#2563eb', badge: 'badge-ahead', label: 'Ahead', icon: '⚡' },
    needs_manual_review: { bg: '#7c3aed', badge: 'badge-review', label: 'Needs Review', icon: '🔍' },
    not_started: { bg: '#4b5563', badge: 'badge-notstarted', label: 'Not Started', icon: '○' }
  };

  return (
    <div className="app-wrapper">
      {/* Top Application Header */}
      {/* Top Application Header */}
      <header className="app-header">
        <div className="container header-container">
          <div className="brand-section">
            <div className="brand-logo-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <div>
              <div className="brand-title">
                BuildLens 4D
                <span className="brand-pill">SRS v1.0 Compliant</span>
              </div>
              <div className="brand-subtitle">
                Field-to-BIM Progress Tracking & Verification System
              </div>
            </div>
          </div>

          <div className="header-controls">
            <div className="mode-toggle">
              <button
                className={`mode-btn ${mode === 'live' ? 'active' : ''}`}
                onClick={() => setMode('live')}
                title="Connect directly to FastAPI Backend on port 8000"
              >
                <span className="mode-label-full">Live Backend</span>
                <span className="mode-label-short">Live</span>
              </button>
              <button
                className={`mode-btn ${mode === 'mock' ? 'active' : ''}`}
                onClick={() => setMode('mock')}
                title="Demonstration Offline Mock Mode"
              >
                <span className="mode-label-full">Mock Demo</span>
                <span className="mode-label-short">Mock</span>
              </button>
            </div>

            <button
              type="button"
              className="api-status-chip api-status-chip-btn"
              onClick={() => {
                setServerConfigInput(apiBaseUrl);
                setShowServerConfigModal(true);
              }}
              title="Server connection & network diagnostics (Tap to configure)"
            >
              <span className={`status-dot ${isApiOnline ? 'dot-online' : 'dot-offline'}`} />
              <span className="status-label status-label-full">
                {isApiOnline ? `Live (${serverLatency ? `${serverLatency}ms` : 'Connected'})` : 'Backend Offline (Tap to Fix)'}
              </span>
              <span className="status-label status-label-short">
                {isApiOnline ? (serverLatency ? `${serverLatency}ms` : 'Live') : 'Offline'}
              </span>
              <span style={{ fontSize: '0.75rem', opacity: 0.7, marginLeft: '3px' }}>⚙️</span>
            </button>

            {!isAppInstalled && (
              <button
                className="install-pwa-btn"
                onClick={handleInstallClick}
                title="Install BuildLens 4D as a Mobile App on your phone"
              >
                📲 <span className="install-label-full">Install App</span>
              </button>
            )}

            <button className="refresh-btn" onClick={() => loadData(mode)} title="Refresh all data">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
              </svg>
              <span>Sync</span>
            </button>
          </div>
        </div>
      </header>

      {/* Primary Feature Tab Bar */}
      <nav className="feature-tabs-bar">
        <div className="container tabs-container">
          <button
            className={`tab-link ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            🏢 4D Schedule & Elements
          </button>
          <button
            className={`tab-link ${activeTab === 'image_verification' ? 'active' : ''}`}
            onClick={() => setActiveTab('image_verification')}
          >
            📸 Verify Building Plan / Image (FR-026/030)
          </button>
          <button
            className={`tab-link ${activeTab === 'scrubber' ? 'active' : ''}`}
            onClick={() => setActiveTab('scrubber')}
          >
            ⏳ 4D Time-Lapse Scrubber
          </button>
          <button
            className={`tab-link ${activeTab === 'review_queue' ? 'active' : ''}`}
            onClick={() => setActiveTab('review_queue')}
          >
            🛡️ Review Queue (FR-022)
            {reviewQueueElements.length > 0 && (
              <span className="tab-counter-badge">{reviewQueueElements.length}</span>
            )}
          </button>
          <button
            className={`tab-link ${activeTab === 'cv_scanner' ? 'active' : ''}`}
            onClick={() => setActiveTab('cv_scanner')}
          >
            👁️ CV Assistance Tool (FR-026)
          </button>
          <button
            className={`tab-link ${activeTab === 'markers' ? 'active' : ''}`}
            onClick={() => setActiveTab('markers')}
          >
            🎯 AR Benchmark Anchors
          </button>
          <button
            className={`tab-link ${activeTab === 'audit_trail' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit_trail')}
          >
            📜 Audit Trail & Logs (FR-025)
          </button>
          <button
            className={`tab-link ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            📊 Reports & Export (FR-030)
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        <div className="container">
          {errorMsg && (
            <div className="error-banner">
              <span>⚠️ {errorMsg}</span>
              <button className="banner-dismiss" onClick={() => setErrorMsg(null)}>✕</button>
            </div>
          )}

          {/* TAB 1: 4D OVERVIEW & SCHEDULE WITH SPATIAL ISOLATOR */}
          {activeTab === 'overview' && (
            <>
              {/* Project Hero Banner */}
              <section className="hero-card">
                <div className="hero-content">
                  <div className="hero-meta">
                    <span className="badge badge-primary">{project.id}</span>
                    <span className="hero-tz">Timezone: {project.timezone || 'UTC'}</span>
                  </div>
                  <h1 className="hero-title">{project.name}</h1>
                  <p className="hero-desc">{project.description}</p>
                </div>
                <div className="hero-progress-section">
                  <div className="progress-radial-label">
                    <span className="progress-value">{summary.completion_percentage}%</span>
                    <span className="progress-sub">4D Schedule Progress</span>
                  </div>
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{ width: `${Math.min(100, summary.completion_percentage)}%` }}
                    />
                  </div>
                </div>
              </section>

              {/* 4D KPI Summary Cards */}
              <section className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-label">Total BIM Elements</div>
                  <div className="kpi-number">{summary.total_elements}</div>
                  <div className="kpi-foot">Structural Scope</div>
                </div>
                <div className="kpi-card" style={{ borderLeft: '4px solid #059669' }}>
                  <div className="kpi-label">Verified Complete</div>
                  <div className="kpi-number" style={{ color: '#059669' }}>{summary.verified_complete}</div>
                  <div className="kpi-foot">Accepted by Field & BIM</div>
                </div>
                <div className="kpi-card" style={{ borderLeft: '4px solid #d97706' }}>
                  <div className="kpi-label">In Progress</div>
                  <div className="kpi-number" style={{ color: '#d97706' }}>{summary.in_progress}</div>
                  <div className="kpi-foot">Active on Site</div>
                </div>
                <div className="kpi-card" style={{ borderLeft: '4px solid #dc2626' }}>
                  <div className="kpi-label">Potentially Delayed</div>
                  <div className="kpi-number" style={{ color: '#dc2626' }}>{summary.potentially_delayed}</div>
                  <div className="kpi-foot">Milestone Overdue</div>
                </div>
                <div className="kpi-card" style={{ borderLeft: '4px solid #7c3aed' }}>
                  <div className="kpi-label">Needs Manual Review</div>
                  <div className="kpi-number" style={{ color: '#7c3aed' }}>{summary.needs_manual_review}</div>
                  <div className="kpi-foot">Occluded or Low Conf.</div>
                </div>
              </section>

              {/* Spatial Floor & Zone Isolator Bar */}
              <section className="isolator-bar">
                <div className="isolator-group">
                  <span className="isolator-label">🏢 Floor Level Isolator:</span>
                  <div className="filter-chips">
                    {['ALL', 'Foundation', 'Ground', 'Mezzanine'].map((lvl) => (
                      <button
                        key={lvl}
                        className={`filter-chip ${selectedFloor === lvl ? 'active' : ''}`}
                        onClick={() => setSelectedFloor(lvl)}
                      >
                        {lvl === 'ALL' ? 'All Storeys' : lvl}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="isolator-group">
                  <span className="isolator-label">📍 Spatial Zone Isolator:</span>
                  <select
                    className="form-select"
                    style={{ width: 'auto', minWidth: '220px', padding: '6px 10px', fontSize: '0.8rem' }}
                    value={selectedZone}
                    onChange={(e) => setSelectedZone(e.target.value)}
                  >
                    <option value="ALL">All Spatial Zones ({elements.length})</option>
                    {uniqueZones.map(z => (
                      <option key={z} value={z}>{z}</option>
                    ))}
                  </select>
                </div>
              </section>

              {/* Elements Explorer Table */}
              <section className="explorer-card">
                <div className="explorer-header">
                  <div>
                    <h2 className="section-title">BIM Elements & 4D Digital Twin</h2>
                    <p className="section-sub">
                      Real-time synchronization with Unity 3D Model ({filteredElements.length} elements shown)
                    </p>
                  </div>
                  <div className="explorer-tools">
                    <input
                      type="text"
                      className="search-input"
                      placeholder="Search ID, label, zone, type..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    <div className="filter-chips">
                      {['ALL', 'verified_complete', 'in_progress', 'needs_manual_review', 'potentially_delayed'].map((flt) => (
                        <button
                          key={flt}
                          className={`filter-chip ${selectedFilter === flt ? 'active' : ''}`}
                          onClick={() => setSelectedFilter(flt)}
                        >
                          {flt.replace(/_/g, ' ')}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="elements-table-wrapper">
                  <div className="desktop-table-view">
                    <table className="elements-table">
                      <thead>
                        <tr>
                          <th>Element ID</th>
                          <th>Type</th>
                          <th>Design Label</th>
                          <th>Spatial Zone</th>
                          <th>4D Schedule Window</th>
                          <th>Verification State</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredElements.map((el) => {
                          const styleInfo = stateColors[el.verification_state] || stateColors.not_started;
                          return (
                            <tr key={el.id}>
                              <td className="element-id-cell">{el.id}</td>
                              <td><span className="type-tag">{el.element_type}</span></td>
                              <td className="label-cell">{el.label}</td>
                              <td className="zone-cell">{el.spatial_zone || 'General'}</td>
                              <td className="schedule-cell">{el.planned_start} → {el.planned_end}</td>
                              <td>
                                <span className={`state-badge ${styleInfo.badge}`}>
                                  <span>{styleInfo.icon}</span>
                                  {styleInfo.label}
                                </span>
                              </td>
                              <td>
                                <button
                                  className="table-action-btn"
                                  onClick={() => handleOpenInspect(el)}
                                >
                                  🔍 Inspect / Evidence
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  {/* Mobile Touch Cards View (Shown on screens < 768px) */}
                  <div className="mobile-cards-view">
                    {filteredElements.length === 0 ? (
                      <div className="mobile-empty-hint">No elements match the current filters.</div>
                    ) : (
                      filteredElements.map((el) => {
                        const styleInfo = stateColors[el.verification_state] || stateColors.not_started;
                        return (
                          <div key={el.id} className="mobile-element-card">
                            <div className="mobile-card-top">
                              <span className="element-id-cell">{el.id}</span>
                              <span className={`state-badge ${styleInfo.badge}`}>
                                <span>{styleInfo.icon}</span>
                                {styleInfo.label}
                              </span>
                            </div>
                            <div className="mobile-card-body">
                              <h4 className="mobile-card-title">{el.label}</h4>
                              <div className="mobile-card-tags">
                                <span className="type-tag">{el.element_type}</span>
                                <span className="zone-pill">{el.spatial_zone || 'General'}</span>
                              </div>
                              <div className="mobile-card-schedule">
                                <span className="sched-icon">📅</span>
                                <span>{el.planned_start} → {el.planned_end}</span>
                              </div>
                            </div>
                            <div className="mobile-card-actions">
                              <button
                                className="mobile-action-btn"
                                onClick={() => handleOpenInspect(el)}
                              >
                                🔍 Inspect / Evidence Photos & 3D Sync
                              </button>
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              </section>
            </>
          )}

          {/* TAB: BUILDING PLAN & IMAGE VERIFICATION (FR-026, FR-027, FR-030) */}
          {activeTab === 'image_verification' && (
            <div className="verification-layout">
              {/* Upload & Configuration Card */}
              <div className="verification-upload-card">
                <div className="verification-header-flex">
                  <div>
                    <h2 className="section-title">Upload Building Plan or Image for 4D Verification</h2>
                    <p className="section-sub">
                      Upload physical site photos, 2D architectural blueprints, or drone surveys to detect structural elements, verify progress against the 4D BIM digital twin, and generate official compliance inspection reports.
                    </p>
                  </div>
                  {verificationResult && (
                    <div className="verification-quick-actions">
                      <a
                        href={verificationResult.report_url.startsWith('http') ? verificationResult.report_url : `${apiBaseUrl.replace('/api', '')}${verificationResult.report_url}`}
                        target="_blank"
                        rel="noreferrer"
                        className="download-report-btn"
                      >
                        🖨️ Open / Print Official PDF Report
                      </a>
                    </div>
                  )}
                </div>

                <form onSubmit={handleRunImageVerification} className="verification-form-grid">
                  {/* File Upload Zone */}
                  <div
                    className={`file-dropzone ${verificationPreviewUrl ? 'has-file' : ''}`}
                    onClick={() => verificationInputRef.current?.click()}
                  >
                    <input
                      type="file"
                      ref={verificationInputRef}
                      accept="image/*,.pdf"
                      onChange={handleSelectVerificationFile}
                      style={{ display: 'none' }}
                    />
                    {verificationPreviewUrl ? (
                      <div className="preview-container">
                        <img src={verificationPreviewUrl} alt="Selected Upload" className="preview-thumbnail" />
                        <div className="change-file-overlay">
                          <span>🔄 Click or Tap to Choose Different Image / Plan</span>
                          <span style={{ fontSize: '0.75rem', opacity: 0.8 }}>({verificationFile?.name})</span>
                        </div>
                      </div>
                    ) : (
                      <div className="dropzone-content">
                        <div className="dropzone-icon">📁</div>
                        <div className="dropzone-title">Click or Tap to Upload Building Plan or Site Photo</div>
                        <div className="dropzone-sub">Supports JPEG, PNG, WEBP, or Architectural Drawings (Camera on Phone Supported)</div>
                      </div>
                    )}
                  </div>

                  {/* Configuration Controls */}
                  <div className="verification-controls">
                    <div className="form-group">
                      <label className="form-label">Classification / Media Type:</label>
                      <select
                        className="form-select"
                        value={verificationPlanType}
                        onChange={(e) => setVerificationPlanType(e.target.value)}
                      >
                        <option value="site_photo">📸 On-Site Physical Building Photo</option>
                        <option value="floor_plan">📐 2D Floor Plan / Blueprint</option>
                        <option value="structural_drawing">🏗️ Structural Engineering Drawing</option>
                        <option value="drone_capture">🚁 Aerial Drone Survey Capture</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Target Spatial Zone:</label>
                      <select
                        className="form-select"
                        value={verificationZone}
                        onChange={(e) => setVerificationZone(e.target.value)}
                      >
                        <option value="ALL">All Spatial Zones (Whole Structure)</option>
                        <option value="Foundation">Foundation & Subsurface Footings</option>
                        <option value="Ground">Ground Floor Grid Columns & Retaining Walls</option>
                        <option value="Mezzanine">Level 1 Mezzanine Concourse & Beams</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label">Inspector / Surveyor ID:</label>
                      <input
                        type="text"
                        className="form-input"
                        value={verificationObserver}
                        onChange={(e) => setVerificationObserver(e.target.value)}
                        required
                      />
                    </div>

                    <button
                      type="submit"
                      className="run-verify-btn"
                      disabled={verificationLoading || !verificationFile}
                    >
                      {verificationLoading ? (
                        <span>⏳ Analyzing Structural Geometry & Matching 4D Milestones...</span>
                      ) : (
                        <span>⚡ Verify Image Against 4D BIM & Generate Audit Report</span>
                      )}
                    </button>
                  </div>
                </form>
              </div>

              {/* Verification Results Viewport & Executive Report */}
              {verificationResult && (
                <div className="verification-results-container">
                  {/* Verdict & Compliance Header Banner */}
                  <div className={`verdict-card ${verificationResult.requires_human_review ? 'verdict-warning' : 'verdict-compliant'}`}>
                    <div className="verdict-left">
                      <div className="verdict-tag">4D BIM VERIFICATION VERDICT:</div>
                      <h3 className="verdict-title">{verificationResult.overall_verdict}</h3>
                      <div className="verdict-sub">
                        Evaluated {verificationResult.total_detected_elements} components against BIM project '{verificationResult.project_id}' milestones.
                      </div>
                    </div>
                    <div className="verdict-right">
                      <div className="compliance-gauge">
                        <div className="gauge-val">{verificationResult.compliance_percentage}%</div>
                        <div className="gauge-label">4D Milestone Compliance</div>
                      </div>
                    </div>
                  </div>

                  {/* AI Building Form & Construction Stage Classifier Badge */}
                  {verificationResult.image_metadata?.ai_model && (
                    <div style={{
                      background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 95, 70, 0.22) 100%)',
                      border: '1px solid rgba(52, 211, 153, 0.35)',
                      borderRadius: '12px',
                      padding: '16px 20px',
                      marginBottom: '20px',
                      boxShadow: '0 4px 16px rgba(0,0,0,0.2)'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '8px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <span style={{ fontSize: '1.4rem' }}>🤖</span>
                          <div>
                            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#6ee7b7', fontWeight: 700 }}>
                              AI Building Recognition Engine
                            </div>
                            <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#f0fdf4' }}>
                              Detected Stage: <span style={{ color: '#34d399' }}>{verificationResult.image_metadata.ai_model.predicted_stage?.replace(/_/g, ' ')}</span>
                            </div>
                          </div>
                        </div>
                        <div style={{ background: 'rgba(52, 211, 153, 0.2)', border: '1px solid #34d399', color: '#6ee7b7', padding: '4px 12px', borderRadius: '20px', fontWeight: 800, fontSize: '0.85rem' }}>
                          Model Confidence: {Math.round((verificationResult.image_metadata.ai_model.stage_confidence || 0.9) * 100)}%
                        </div>
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#d1fae5', marginBottom: '12px', lineHeight: 1.5 }}>
                        {verificationResult.image_metadata.ai_model.stage_description}
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', fontSize: '0.75rem' }}>
                        <span style={{ background: 'rgba(0,0,0,0.35)', padding: '3px 10px', borderRadius: '6px', color: '#93c5fd', border: '1px solid rgba(147, 197, 253, 0.2)' }}>
                          Concrete Ratio: <strong>{Math.round((verificationResult.image_metadata.ai_model.visual_metrics?.concrete_ratio || 0.3) * 100)}%</strong>
                        </span>
                        <span style={{ background: 'rgba(0,0,0,0.35)', padding: '3px 10px', borderRadius: '6px', color: '#fde047', border: '1px solid rgba(253, 224, 71, 0.2)' }}>
                          Earthwork/Soil: <strong>{Math.round((verificationResult.image_metadata.ai_model.visual_metrics?.earth_tone_ratio || 0.1) * 100)}%</strong>
                        </span>
                        <span style={{ background: 'rgba(0,0,0,0.35)', padding: '3px 10px', borderRadius: '6px', color: '#c4b5fd', border: '1px solid rgba(196, 181, 253, 0.2)' }}>
                          Structural Edge Density: <strong>{verificationResult.image_metadata.ai_model.visual_metrics?.v_edge_density || '0.07'}</strong>
                        </span>
                        <span style={{
                          background: verificationResult.image_metadata.ai_model.scaffolding_detected ? 'rgba(239, 68, 68, 0.25)' : 'rgba(16, 185, 129, 0.25)',
                          padding: '3px 10px',
                          borderRadius: '6px',
                          color: verificationResult.image_metadata.ai_model.scaffolding_detected ? '#fca5a5' : '#86efac',
                          border: verificationResult.image_metadata.ai_model.scaffolding_detected ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid rgba(16, 185, 129, 0.4)',
                          fontWeight: 700
                        }}>
                          {verificationResult.image_metadata.ai_model.scaffolding_detected ? '⚠️ Scaffolding Occlusion Flagged (SRS 8.3)' : '✓ Line of Sight Unobstructed'}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Summary Metric Cards */}
                  <div className="verification-metrics-grid">
                    <div className="kpi-card">
                      <div className="kpi-label">Detected Elements</div>
                      <div className="kpi-number" style={{ color: '#38bdf8' }}>{verificationResult.total_detected_elements}</div>
                      <div className="kpi-foot">Structural Components</div>
                    </div>
                    <div className="kpi-card" style={{ borderLeft: '4px solid #059669' }}>
                      <div className="kpi-label">Verified Complete</div>
                      <div className="kpi-number" style={{ color: '#059669' }}>{verificationResult.verified_complete_count}</div>
                      <div className="kpi-foot">Conforms to Schedule</div>
                    </div>
                    <div className="kpi-card" style={{ borderLeft: '4px solid #d97706' }}>
                      <div className="kpi-label">In Progress</div>
                      <div className="kpi-number" style={{ color: '#d97706' }}>{verificationResult.in_progress_count}</div>
                      <div className="kpi-foot">Active on Site</div>
                    </div>
                    <div className="kpi-card" style={{ borderLeft: '4px solid #7c3aed' }}>
                      <div className="kpi-label">Human Review Needed</div>
                      <div className="kpi-number" style={{ color: '#7c3aed' }}>{verificationResult.occluded_review_count}</div>
                      <div className="kpi-foot">SRS 8.3 Occlusion Alert</div>
                    </div>
                  </div>

                  {/* Visual Detection Overlay Viewport */}
                  <div className="visual-inspection-card">
                    <div className="inspection-card-header">
                      <h3 className="panel-title">Visual Detection & Bounding Box Overlays</h3>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        SHA-256: {verificationResult.file_hash.substring(0, 16)}... &bull; Resolution: {verificationResult.image_metadata?.width}x{verificationResult.image_metadata?.height}px
                      </span>
                    </div>

                    <div className="interactive-overlay-viewport">
                      <img
                        src={verificationResult.media_url.startsWith('http') ? verificationResult.media_url : `${apiBaseUrl.replace('/api', '')}${verificationResult.media_url}`}
                        alt="Analyzed Building"
                        className="analyzed-base-img"
                      />
                      {verificationResult.elements.map((el) => {
                        const [bx, by, bw, bh] = el.bounding_box;
                        const statusColors = {
                          verified_complete: '#059669',
                          in_progress: '#d97706',
                          potentially_delayed: '#dc2626',
                          needs_manual_review: '#7c3aed',
                          not_started: '#64748b'
                        };
                        const color = statusColors[el.visual_status] || '#38bdf8';
                        return (
                          <div
                            key={el.element_id}
                            className="detection-bbox"
                            style={{
                              left: `${bx * 100}%`,
                              top: `${by * 100}%`,
                              width: `${bw * 100}%`,
                              height: `${bh * 100}%`,
                              borderColor: color
                            }}
                          >
                            <span className="bbox-label-tag" style={{ background: color }}>
                              {el.element_id} [{(el.confidence_score * 100).toFixed(0)}%]
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Discrepancy Breakdown Table & Cards */}
                  <div className="explorer-card" style={{ marginTop: '20px' }}>
                    <div className="explorer-header">
                      <div>
                        <h3 className="section-title">Element Discrepancy & Verification Audit Breakdown</h3>
                        <p className="section-sub">
                          Comparing visible as-built state vs. planned 4D construction milestone dates.
                        </p>
                      </div>
                      <a
                        href={verificationResult.report_url.startsWith('http') ? verificationResult.report_url : `${apiBaseUrl.replace('/api', '')}${verificationResult.report_url}`}
                        target="_blank"
                        rel="noreferrer"
                        className="download-report-btn"
                      >
                        🖨️ View & Print Full Official Report
                      </a>
                    </div>

                    <div className="elements-table-wrapper">
                      <div className="desktop-table-view">
                        <table className="elements-table">
                          <thead>
                            <tr>
                              <th>Element ID</th>
                              <th>Type</th>
                              <th>Design Label</th>
                              <th>Spatial Zone</th>
                              <th>4D Milestone Window</th>
                              <th>Observed Status</th>
                              <th>Confidence</th>
                              <th>Verification Notes</th>
                            </tr>
                          </thead>
                          <tbody>
                            {verificationResult.elements.map((el) => {
                              const styleInfo = stateColors[el.visual_status] || stateColors.not_started;
                              return (
                                <tr key={el.element_id}>
                                  <td className="element-id-cell">{el.element_id}</td>
                                  <td><span className="type-tag">{el.element_type}</span></td>
                                  <td className="label-cell">{el.label}</td>
                                  <td className="zone-cell">{el.spatial_zone}</td>
                                  <td className="schedule-cell">{el.planned_start} → {el.planned_end}</td>
                                  <td>
                                    <span className={`state-badge ${styleInfo.badge}`}>
                                      <span>{styleInfo.icon}</span>
                                      {styleInfo.label}
                                    </span>
                                  </td>
                                  <td><strong>{(el.confidence_score * 100).toFixed(0)}%</strong></td>
                                  <td style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{el.notes}</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>

                      <div className="mobile-cards-view">
                        {verificationResult.elements.map((el) => {
                          const styleInfo = stateColors[el.visual_status] || stateColors.not_started;
                          return (
                            <div key={el.element_id} className="mobile-element-card">
                              <div className="mobile-card-top">
                                <span className="element-id-cell">{el.element_id}</span>
                                <span className={`state-badge ${styleInfo.badge}`}>
                                  <span>{styleInfo.icon}</span>
                                  {styleInfo.label}
                                </span>
                              </div>
                              <div className="mobile-card-body">
                                <h4 className="mobile-card-title">{el.label}</h4>
                                <div className="mobile-card-tags">
                                  <span className="type-tag">{el.element_type}</span>
                                  <span className="zone-pill">{el.spatial_zone}</span>
                                  <span style={{ fontSize: '0.72rem', color: '#38bdf8' }}>
                                    Conf: {(el.confidence_score * 100).toFixed(0)}%
                                  </span>
                                </div>
                                <div className="mobile-card-schedule">
                                  <span>📅 {el.planned_start} → {el.planned_end}</span>
                                </div>
                                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', background: 'rgba(0,0,0,0.3)', padding: '6px 8px', borderRadius: '4px' }}>
                                  {el.notes}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Past Verification Reports History */}
              {verificationHistory.length > 0 && (
                <div className="explorer-card" style={{ marginTop: '24px' }}>
                  <div className="explorer-header">
                    <div>
                      <h3 className="section-title">Verified Inspection Reports History ({verificationHistory.length})</h3>
                      <p className="section-sub">Immutable audit records of all previous building image and plan verifications.</p>
                    </div>
                  </div>
                  <div className="verification-history-grid">
                    {verificationHistory.map((rep) => (
                      <div key={rep.id} className="history-report-card">
                        <div className="history-card-header">
                          <span className="queue-id">{rep.id}</span>
                          <span className="type-tag">{rep.plan_type.replace('_', ' ').toUpperCase()}</span>
                        </div>
                        <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)', margin: '6px 0' }}>
                          {rep.overall_verdict}
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          <span>Compliance: <strong style={{ color: '#38bdf8' }}>{rep.compliance_percentage}%</strong></span>
                          <span>{new Date(rep.created_at).toLocaleDateString()}</span>
                        </div>
                        <a
                          href={rep.report_url.startsWith('http') ? rep.report_url : `${apiBaseUrl.replace('/api', '')}${rep.report_url}`}
                          target="_blank"
                          rel="noreferrer"
                          className="history-view-link"
                        >
                          📄 Open Full Report
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: 4D TIME-LAPSE SCHEDULE SCRUBBER */}
          {activeTab === 'scrubber' && (
            <div className="scrubber-layout">
              <div className="scrubber-control-card">
                <div className="scrubber-header-flex">
                  <div>
                    <h2 className="section-title">4D Time-Lapse Schedule Scrubber</h2>
                    <p className="section-sub">
                      Simulate 4D construction milestone evolution across past, present, and scheduled dates.
                    </p>
                  </div>
                  <div className="scrubber-actions">
                    <button
                      className={`play-scrub-btn ${isPlayingScrubber ? 'btn-pause' : 'btn-play'}`}
                      onClick={() => setIsPlayingScrubber(!isPlayingScrubber)}
                    >
                      {isPlayingScrubber ? '⏸ Pause Simulation' : '▶ Play 4D Simulation'}
                    </button>
                  </div>
                </div>

                <div className="scrubber-slider-wrapper">
                  <div className="scrubber-slider-header">
                    <span>Simulated Date: <strong style={{ color: '#38bdf8', fontSize: '1.2rem' }}>{scrubberDate}</strong></span>
                    <input
                      type="date"
                      value={scrubberDate}
                      onChange={(e) => setScrubberDate(e.target.value)}
                      className="form-input"
                      style={{ width: 'auto', padding: '4px 10px' }}
                    />
                  </div>
                  <input
                    type="range"
                    min="1723680000000" // 2026-08-15
                    max="1731628800000" // 2026-11-15
                    step="86400000"     // 1 day
                    value={new Date(scrubberDate).getTime()}
                    onChange={(e) => setScrubberDate(new Date(parseInt(e.target.value)).toISOString().split('T')[0])}
                    className="range-slider"
                  />
                  <div className="slider-labels">
                    <span>Aug 15, 2026 (Foundation)</span>
                    <span>Oct 01 (Structural Frame)</span>
                    <span>Nov 15, 2026 (Completion)</span>
                  </div>
                </div>

                {simulationData && (
                  <div className="simulation-kpi-row">
                    <div className="kpi-mini">
                      <div className="kpi-label">Projected Progress</div>
                      <div className="kpi-number" style={{ color: '#38bdf8' }}>
                        {simulationData.simulated_completion_percentage}%
                      </div>
                    </div>
                    <div className="kpi-mini">
                      <div className="kpi-label">Completed on Date</div>
                      <div className="kpi-number" style={{ color: '#059669' }}>
                        {simulationData.completed_elements} / {simulationData.total_elements}
                      </div>
                    </div>
                    <div className="kpi-mini">
                      <div className="kpi-label">Active Construction</div>
                      <div className="kpi-number" style={{ color: '#d97706' }}>
                        {simulationData.in_progress_elements}
                      </div>
                    </div>
                    <div className="kpi-mini">
                      <div className="kpi-label">Pending Start</div>
                      <div className="kpi-number" style={{ color: '#64748b' }}>
                        {simulationData.not_started_elements}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Simulated Elements Grid */}
              <div className="explorer-card" style={{ marginTop: '20px' }}>
                <h3 className="panel-title" style={{ padding: '20px 24px 0' }}>
                  Simulated 4D Element States as of {scrubberDate}
                </h3>
                <div className="elements-table-wrapper">
                  <div className="desktop-table-view">
                    <table className="elements-table">
                      <thead>
                        <tr>
                          <th>Element ID</th>
                          <th>Type</th>
                          <th>Spatial Zone</th>
                          <th>Planned Milestone</th>
                          <th>Simulated State on {scrubberDate}</th>
                          <th>Progress %</th>
                        </tr>
                      </thead>
                      <tbody>
                        {simulationData?.elements?.map((el) => {
                          const styleInfo = stateColors[el.simulated_state] || stateColors.not_started;
                          return (
                            <tr key={el.id} style={{ background: el.is_active_on_date ? 'rgba(217, 119, 6, 0.08)' : 'transparent' }}>
                              <td className="element-id-cell">{el.id}</td>
                              <td><span className="type-tag">{el.element_type}</span></td>
                              <td className="zone-cell">{el.spatial_zone}</td>
                              <td className="schedule-cell">{el.planned_start} → {el.planned_end}</td>
                              <td>
                                <span className={`state-badge ${styleInfo.badge}`}>
                                  <span>{styleInfo.icon}</span>
                                  {styleInfo.label}
                                </span>
                              </td>
                              <td>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                  <div style={{ width: '80px', height: '6px', background: '#334155', borderRadius: '3px', overflow: 'hidden' }}>
                                    <div style={{ width: `${el.simulated_progress_percentage}%`, height: '100%', background: '#38bdf8' }} />
                                  </div>
                                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{el.simulated_progress_percentage}%</span>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  <div className="mobile-cards-view">
                    {simulationData?.elements?.map((el) => {
                      const styleInfo = stateColors[el.simulated_state] || stateColors.not_started;
                      return (
                        <div key={el.id} className="mobile-element-card" style={{ borderColor: el.is_active_on_date ? '#f59e0b' : 'var(--border-subtle)' }}>
                          <div className="mobile-card-top">
                            <span className="element-id-cell">{el.id}</span>
                            <span className={`state-badge ${styleInfo.badge}`}>
                              <span>{styleInfo.icon}</span>
                              {styleInfo.label}
                            </span>
                          </div>
                          <div className="mobile-card-body">
                            <div className="mobile-card-tags">
                              <span className="type-tag">{el.element_type}</span>
                              <span className="zone-pill">{el.spatial_zone}</span>
                            </div>
                            <div className="mobile-card-schedule">
                              <span>📅 Planned: {el.planned_start} → {el.planned_end}</span>
                            </div>
                            <div style={{ marginTop: '10px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '5px' }}>
                                <span>Simulated 4D Progress:</span>
                                <strong style={{ color: '#38bdf8' }}>{el.simulated_progress_percentage}%</strong>
                              </div>
                              <div style={{ width: '100%', height: '8px', background: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
                                <div style={{ width: `${el.simulated_progress_percentage}%`, height: '100%', background: 'linear-gradient(90deg, #0ea5e9, #10b981)' }} />
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: MANUAL REVIEW QUEUE (SRS FR-022, FR-024) */}
          {activeTab === 'review_queue' && (
            <div className="review-queue-layout">
              <div className="queue-list-section">
                <div className="section-title-box">
                  <h2 className="section-title">Manual Review Queue (SRS FR-022)</h2>
                  <p className="section-sub">
                    Elements flagged due to occlusion, borderline CV confidence, or disputed milestone progress.
                  </p>
                </div>

                {reviewQueueElements.length === 0 ? (
                  <div className="empty-state-card">
                    <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🎉</div>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Review Queue Clear!</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      No elements currently require manual intervention or occlusion clearance.
                    </div>
                  </div>
                ) : (
                  <div className="queue-cards-list">
                    {reviewQueueElements.map((el) => (
                      <div
                        key={el.id}
                        className={`queue-card ${selectedReviewElement?.id === el.id ? 'active' : ''}`}
                        onClick={() => setSelectedReviewElement(el)}
                      >
                        <div className="queue-card-header">
                          <span className="queue-id">{el.id}</span>
                          <span className={`state-badge ${stateColors[el.verification_state]?.badge}`}>
                            {stateColors[el.verification_state]?.label}
                          </span>
                        </div>
                        <div className="queue-card-label">{el.label}</div>
                        <div className="queue-card-meta">
                          <span>Zone: {el.spatial_zone || 'General'}</span>
                          <span>•</span>
                          <span>Planned: {el.planned_start} to {el.planned_end}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Review Decision Workspace Form (FR-024) */}
              <div className="review-form-section">
                <div className="decision-panel">
                  <h3 className="panel-title">BIM Coordinator Verdict Panel</h3>
                  <p className="panel-sub">
                    SRS 8.1 Rule: Every status transition must include auditable reviewer attribution and justification.
                  </p>

                  {selectedReviewElement ? (
                    <form onSubmit={handleSubmitReviewDecision} className="verdict-form">
                      <div className="target-summary-box">
                        <div className="target-label">Selected Target:</div>
                        <div className="target-title">{selectedReviewElement.id} - {selectedReviewElement.label}</div>
                        <div className="target-status">Current Status: {selectedReviewElement.verification_state}</div>
                      </div>

                      <div className="form-group">
                        <label className="form-label">Reviewer ID / Sign-off Authority:</label>
                        <input
                          type="text"
                          className="form-input"
                          value={reviewerId}
                          onChange={(e) => setReviewerId(e.target.value)}
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">Review Outcome Decision (SRS FR-024):</label>
                        <div className="decision-radio-grid">
                          <label className={`radio-card ${reviewDecisionType === 'confirmed' ? 'active' : ''}`}>
                            <input
                              type="radio"
                              name="decision"
                              value="confirmed"
                              checked={reviewDecisionType === 'confirmed'}
                              onChange={(e) => setReviewDecisionType(e.target.value)}
                            />
                            <div>
                              <div className="radio-head">✓ Confirmed (Accept)</div>
                              <div className="radio-desc">Sets state to Verified Complete</div>
                            </div>
                          </label>

                          <label className={`radio-card ${reviewDecisionType === 'rejected' ? 'active' : ''}`}>
                            <input
                              type="radio"
                              name="decision"
                              value="rejected"
                              checked={reviewDecisionType === 'rejected'}
                              onChange={(e) => setReviewDecisionType(e.target.value)}
                            />
                            <div>
                              <div className="radio-head">✕ Rejected (Delayed)</div>
                              <div className="radio-desc">Flags element as Potentially Delayed</div>
                            </div>
                          </label>

                          <label className={`radio-card ${reviewDecisionType === 'corrected' ? 'active' : ''}`}>
                            <input
                              type="radio"
                              name="decision"
                              value="corrected"
                              checked={reviewDecisionType === 'corrected'}
                              onChange={(e) => setReviewDecisionType(e.target.value)}
                            />
                            <div>
                              <div className="radio-head">⏳ Corrected (In Progress)</div>
                              <div className="radio-desc">Confirmed partially installed</div>
                            </div>
                          </label>

                          <label className={`radio-card ${reviewDecisionType === 'rescan_requested' ? 'active' : ''}`}>
                            <input
                              type="radio"
                              name="decision"
                              value="rescan_requested"
                              checked={reviewDecisionType === 'rescan_requested'}
                              onChange={(e) => setReviewDecisionType(e.target.value)}
                            />
                            <div>
                              <div className="radio-head">🔄 Request Rescan</div>
                              <div className="radio-desc">Requests secondary AR capture</div>
                            </div>
                          </label>
                        </div>
                      </div>

                      <div className="form-group">
                        <label className="form-label">Justification Rationale (Immutable Audit Log):</label>
                        <textarea
                          className="form-textarea"
                          rows="4"
                          value={reviewReason}
                          onChange={(e) => setReviewReason(e.target.value)}
                          required
                          placeholder="State reasoning, photographic evidence references, or engineering site notes..."
                        />
                      </div>

                      <button
                        type="submit"
                        className="submit-verdict-btn"
                        disabled={reviewSubmitting}
                      >
                        {reviewSubmitting ? 'Recording Decision...' : 'Commit Review Decision (Syncs to Unity)'}
                      </button>
                    </form>
                  ) : (
                    <div className="empty-panel-prompt">
                      Select an element from the queue on the left to initiate the review decision workflow.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: COMPUTER VISION SCANNER & GUARDRAIL TOOL (SRS FR-026, FR-027, SRS 8.3) */}
          {activeTab === 'cv_scanner' && (
            <div className="cv-scanner-layout">
              <div className="cv-simulator-card">
                <h2 className="section-title">AI Computer Vision Assistive Engine</h2>
                <p className="section-sub">
                  Simulates neural object detection and evaluates Section 8.3 Guardrails (Automated proposals are assistive only).
                </p>

                <div className="cv-controls-grid">
                  <div className="form-group">
                    <label className="form-label">Target BIM Element:</label>
                    <select
                      className="form-select"
                      value={cvTargetElementId}
                      onChange={(e) => setCvTargetElementId(e.target.value)}
                    >
                      {elements.map((el) => (
                        <option key={el.id} value={el.id}>
                          {el.id} — {el.label} ({el.verification_state})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">
                      Simulated Detection Confidence: <strong>{(cvConfidence * 100).toFixed(0)}%</strong>
                    </label>
                    <input
                      type="range"
                      min="0.20"
                      max="0.99"
                      step="0.05"
                      value={cvConfidence}
                      onChange={(e) => setCvConfidence(e.target.value)}
                      className="range-slider"
                    />
                    <div className="slider-labels">
                      <span>Low (&lt;60%)</span>
                      <span>Guardrail Threshold (60%)</span>
                      <span>High (&gt;80%)</span>
                    </div>
                  </div>

                  <div className="form-group checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={cvOccluded}
                        onChange={(e) => setCvOccluded(e.target.checked)}
                      />
                      <span>Simulate Visual Occlusion (e.g. Scaffolding, Canvas, Crane)</span>
                    </label>
                  </div>

                  <button
                    className="run-cv-btn"
                    onClick={handleRunCVAnalysis}
                    disabled={cvAnalyzing}
                  >
                    {cvAnalyzing ? 'Analyzing Frame...' : '⚡ Run CV Detection & Apply Guardrails'}
                  </button>
                </div>
              </div>

              {/* CV Output & Bounding Box Visualization */}
              <div className="cv-display-card">
                <h3 className="panel-title">Computer Vision Proposal Viewport</h3>
                {cvResult ? (
                  <div className="cv-result-container">
                    <div className="camera-viewport-mock">
                      <div className="viewport-overlay-frame">
                        <div
                          className="cv-bounding-box"
                          style={{
                            left: `${cvResult.proposals[0]?.bounding_box[0] * 100}%`,
                            top: `${cvResult.proposals[0]?.bounding_box[1] * 100}%`,
                            width: `${cvResult.proposals[0]?.bounding_box[2] * 100}%`,
                            height: `${cvResult.proposals[0]?.bounding_box[3] * 100}%`,
                            borderColor: cvResult.requires_human_review ? '#f59e0b' : '#10b981'
                          }}
                        >
                          <span className="bbox-label">
                            {cvResult.proposals[0]?.element_id} [{(cvResult.proposals[0]?.confidence_score * 100).toFixed(0)}%]
                          </span>
                        </div>
                      </div>
                      <div className="viewport-hud">
                        <span>FOV: 78°</span>
                        <span>POSE: [X: 1.2m, Y: 1.6m, Z: 4.8m]</span>
                        <span>STATUS: {cvResult.proposals[0]?.visual_state_proposed}</span>
                      </div>
                    </div>

                    <div className={`guardrail-alert ${cvResult.requires_human_review ? 'alert-warning' : 'alert-success'}`}>
                      <div className="alert-head">
                        {cvResult.requires_human_review ? '⚠️ SRS 8.3 GUARDRAIL TRIGGERED' : '✓ HIGH CONFIDENCE DETECTION'}
                      </div>
                      <div className="alert-text">{cvResult.explanation}</div>
                      <div className="alert-rule">
                        <strong>Rule: </strong>{cvResult.proposals[0]?.guardrail_note}
                      </div>
                    </div>

                    <div className="cv-actions">
                      <button
                        className="action-btn"
                        style={{ background: '#7c3aed', color: 'white' }}
                        onClick={() => {
                          handleUpdateObservation(
                            cvTargetElementId,
                            cvResult.requires_human_review ? 'occluded' : 'accepted_complete',
                            `CV Proposal imported: ${cvResult.proposals[0]?.guardrail_note}`
                          );
                          setActiveTab('review_queue');
                        }}
                      >
                        Route to Review Queue
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="empty-panel-prompt">
                    Click "Run CV Detection" above to test automated BIM object detection proposals and verify safety rules.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 5: AR BENCHMARK ANCHORS & QR FIDUCIALS */}
          {activeTab === 'markers' && (
            <div className="markers-layout">
              <div className="markers-list-card">
                <h2 className="section-title">AR Site Benchmark Anchors</h2>
                <p className="section-sub">
                  Survey-grade fiducial coordinates for sub-centimeter mobile AR alignment on physical construction slabs.
                </p>

                <div className="benchmark-items-grid">
                  {benchmarks.map((bm) => (
                    <div
                      key={bm.marker_id}
                      className={`benchmark-card ${selectedBenchmark?.marker_id === bm.marker_id ? 'active' : ''}`}
                      onClick={() => setSelectedBenchmark(bm)}
                    >
                      <div className="benchmark-card-header">
                        <span className="queue-id">{bm.marker_id}</span>
                        <span className="type-tag">{bm.zone}</span>
                      </div>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)', margin: '4px 0' }}>{bm.label}</div>
                      <div className="benchmark-coords">
                        <span>N: {bm.northing_m.toFixed(3)}m</span>
                        <span>E: {bm.easting_m.toFixed(3)}m</span>
                        <span>Z: {bm.elevation_m.toFixed(3)}m</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Benchmark Target Display & SVG Preview */}
              {selectedBenchmark && (
                <div className="marker-preview-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 className="panel-title">{selectedBenchmark.marker_id} Surveyor Target Card</h3>
                    <a
                      href={`${apiBaseUrl}/projects/proj-terminal-04/markers/${selectedBenchmark.marker_id}/svg`}
                      target="_blank"
                      rel="noreferrer"
                      className="download-csv-btn"
                      style={{ padding: '6px 14px', fontSize: '0.8rem' }}
                    >
                      ⬇ Print SVG Target
                    </a>
                  </div>

                  <div className="target-svg-wrapper">
                    <img
                      src={`${apiBaseUrl}/projects/proj-terminal-04/markers/${selectedBenchmark.marker_id}/svg`}
                      alt="Survey Target"
                      className="target-svg-img"
                    />
                  </div>

                  <div className="benchmark-details-box">
                    <div className="form-group">
                      <label className="form-label">QR Decoded Payload for AR Camera:</label>
                      <input
                        type="text"
                        readOnly
                        value={selectedBenchmark.qr_payload}
                        className="form-input"
                        style={{ fontFamily: 'monospace', fontSize: '0.78rem' }}
                      />
                    </div>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                      {selectedBenchmark.description}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 6: AUDIT TRAIL & GOVERNANCE (SRS FR-025) */}
          {activeTab === 'audit_trail' && (
            <section className="explorer-card">
              <div className="explorer-header">
                <div>
                  <h2 className="section-title">Audit Trail & Compliance Log (SRS FR-025)</h2>
                  <p className="section-sub">
                    Immutable chronological record of all inspections, human verdicts, and 4D state transitions.
                  </p>
                </div>
              </div>

              {auditLogs.length === 0 ? (
                <div className="empty-state-card">
                  <div>📜 No audit log entries recorded yet for this project.</div>
                </div>
              ) : (
                <div className="elements-table-wrapper">
                  <div className="desktop-table-view">
                    <table className="elements-table">
                      <thead>
                        <tr>
                          <th>Timestamp (UTC)</th>
                          <th>Actor</th>
                          <th>Action</th>
                          <th>Entity ID</th>
                          <th>Details / Rationale</th>
                        </tr>
                      </thead>
                      <tbody>
                        {auditLogs.map((log) => (
                          <tr key={log.id}>
                            <td style={{ whiteSpace: 'nowrap', color: 'var(--text-muted)' }}>
                              {new Date(log.created_at).toLocaleString()}
                            </td>
                            <td style={{ fontWeight: 600, color: '#38bdf8' }}>{log.actor_id}</td>
                            <td>
                              <span className="type-tag">{log.action}</span>
                            </td>
                            <td className="element-id-cell">{log.entity_id}</td>
                            <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                              {log.details_json}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="mobile-cards-view">
                    {auditLogs.map((log) => (
                      <div key={log.id} className="mobile-element-card">
                        <div className="mobile-card-top">
                          <span className="type-tag">{log.action}</span>
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                            {new Date(log.created_at).toLocaleDateString()} {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        <div className="mobile-card-body">
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '6px' }}>
                            <span className="element-id-cell">{log.entity_id}</span>
                            <span style={{ fontSize: '0.78rem', color: '#38bdf8' }}>by {log.actor_id}</span>
                          </div>
                          <div className="mobile-audit-details">
                            {log.details_json}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </section>
          )}

          {/* TAB 7: REPORTS & CSV EXPORT (SRS FR-030) */}
          {activeTab === 'reports' && (
            <div className="reports-layout">
              <div className="export-action-card">
                <div>
                  <h2 className="section-title">4D Progress Report & Data Export (FR-030)</h2>
                  <p className="section-sub">
                    Export verified element milestone states, inspection timestamps, and zone distributions.
                  </p>
                </div>
                <a
                  href={`${apiBaseUrl}/projects/proj-terminal-04/export/csv`}
                  target="_blank"
                  rel="noreferrer"
                  className="download-csv-btn"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
                  </svg>
                  Download Progress Report (CSV)
                </a>
              </div>

              {governanceData && (
                <div className="governance-grid">
                  <div className="kpi-card">
                    <div className="kpi-label">Human Review Decisions</div>
                    <div className="kpi-number" style={{ color: '#0284c7' }}>
                      {governanceData.governance?.total_human_reviews ?? reviewDecisions.length}
                    </div>
                    <div className="kpi-foot">Verified Sign-offs</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-label">Total Audit Events</div>
                    <div className="kpi-number" style={{ color: '#10b981' }}>
                      {governanceData.governance?.total_audit_events ?? auditLogs.length}
                    </div>
                    <div className="kpi-foot">Immutable Records</div>
                  </div>
                  <div className="kpi-card" style={{ gridColumn: 'span 2' }}>
                    <div className="kpi-label">SRS Specification Standard</div>
                    <div style={{ marginTop: '8px', fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                      BuildLens4D_SRS.docx (Section 4 & Section 8.3)
                    </div>
                    <div className="kpi-foot" style={{ color: '#059669', marginTop: '4px' }}>
                      ✓ 100% Core Requirements Implemented
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Inspect Element Modal with Evidence Photo Gallery & Field Uploader */}
      {inspectElement && (
        <div className="modal-backdrop" onClick={() => setInspectElement(null)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3>BIM Element: {inspectElement.id}</h3>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{inspectElement.label}</div>
              </div>
              <button className="close-btn" onClick={() => setInspectElement(null)}>✕</button>
            </div>

            <div className="modal-grid">
              <div>
                <div className="modal-field-label">Element Type</div>
                <div className="modal-field-value">{inspectElement.element_type}</div>
              </div>
              <div>
                <div className="modal-field-label">Verification State</div>
                <div className="modal-field-value" style={{ textTransform: 'capitalize' }}>
                  {inspectElement.verification_state.replace(/_/g, ' ')}
                </div>
              </div>
              <div>
                <div className="modal-field-label">Spatial Zone</div>
                <div className="modal-field-value">{inspectElement.spatial_zone || 'Unassigned'}</div>
              </div>
              <div>
                <div className="modal-field-label">4D Milestone</div>
                <div className="modal-field-value">{inspectElement.planned_start} → {inspectElement.planned_end}</div>
              </div>
            </div>

            {/* Field Photographic Evidence Gallery */}
            <div className="evidence-section-box">
              <div className="evidence-header-flex">
                <span className="modal-field-label">📸 Field Photographic Evidence Gallery ({elementEvidences.length})</span>
                {evidenceLoading && <span style={{ fontSize: '0.72rem', color: '#38bdf8' }}>Loading media...</span>}
              </div>

              {elementEvidences.length > 0 ? (
                <div className="evidence-thumbnails-grid">
                  {elementEvidences.map((evi) => (
                    <div key={evi.id} className="evidence-thumb-card">
                      <img src={evi.media_url.startsWith('http') ? evi.media_url : `${apiBaseUrl.replace('/api', '')}${evi.media_url}`} alt="Site Evidence" className="evidence-img" />
                      <div className="evidence-meta">
                        <div>{new Date(evi.captured_at).toLocaleDateString()}</div>
                        <div style={{ fontFamily: 'monospace', fontSize: '0.65rem' }}>SHA: {evi.file_hash.substring(0, 8)}...</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-evidence-prompt">
                  No photographic evidence uploaded yet for this element. Attach a site inspection photo below.
                </div>
              )}

              {/* Upload New Field Photo */}
              <form onSubmit={handleUploadEvidence} className="upload-evidence-form">
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  + Upload New Site Inspection Photo
                </div>
                <div className="upload-evidence-grid">
                  <input
                    type="file"
                    ref={fileInputRef}
                    accept="image/*"
                    className="form-input"
                    style={{ padding: '6px' }}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Inspector ID (e.g. eng_field_01)"
                    value={uploadObserver}
                    onChange={(e) => setUploadObserver(e.target.value)}
                    className="form-input"
                    required
                  />
                </div>
                <div className="upload-evidence-note-row">
                  <input
                    type="text"
                    placeholder="Inspection note or rebar verification detail..."
                    value={uploadNotes}
                    onChange={(e) => setUploadNotes(e.target.value)}
                    className="form-input"
                  />
                  <button
                    type="submit"
                    className="upload-submit-btn"
                    disabled={uploadingEvidence}
                  >
                    {uploadingEvidence ? 'Uploading...' : 'Upload Evidence'}
                  </button>
                </div>
              </form>
            </div>

            {/* Realtime 3D Model Synchronization Actions */}
            <div className="modal-sync-section">
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px' }}>
                🚀 LIVE 3D BIM ACTION (Syncs to Unity Model in Real-Time):
              </div>
              <div className="modal-bim-actions">
                <button
                  className="modal-bim-btn btn-verify-complete"
                  onClick={() => handleUpdateObservation(inspectElement.id, 'accepted_complete', 'Inspected on-site; rebar and concrete curing verified complete.')}
                >
                  ✓ Verify Complete
                </button>
                <button
                  className="modal-bim-btn btn-in-progress"
                  onClick={() => handleUpdateObservation(inspectElement.id, 'in_progress', 'Formwork currently erected; rebar placement in progress.')}
                >
                  ⏳ In Progress
                </button>
                <button
                  className="modal-bim-btn btn-occluded"
                  onClick={() => handleUpdateObservation(inspectElement.id, 'occluded', 'Element occluded by scaffolding; requires manual review.')}
                >
                  ⚠ Flag Occluded (Review)
                </button>
                <button
                  className="modal-bim-btn btn-delayed"
                  onClick={() => handleUpdateObservation(inspectElement.id, 'missing', 'Element behind schedule; milestone date exceeded.')}
                >
                  ✖ Flag Delayed
                </button>
              </div>
            </div>

            <div className="modal-footer-row">
              <button className="action-btn modal-dismiss-btn" onClick={() => setInspectElement(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* PWA Mobile App Install Guide Modal */}
      {showInstallGuide && (
        <div className="modal-backdrop" onClick={() => setShowInstallGuide(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px' }}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '1.5rem' }}>📲</span>
                <h3 style={{ margin: 0 }}>Install BuildLens 4D Mobile App</h3>
              </div>
              <button className="close-btn" onClick={() => setShowInstallGuide(false)}>✕</button>
            </div>

            <div style={{ padding: '8px 0', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              <p style={{ marginBottom: '16px' }}>
                You can install BuildLens 4D as a full-screen native mobile application directly on your phone:
              </p>

              <div style={{ background: 'rgba(2, 132, 199, 0.1)', border: '1px solid rgba(2, 132, 199, 0.3)', borderRadius: '8px', padding: '14px', marginBottom: '12px' }}>
                <div style={{ fontWeight: 700, color: '#38bdf8', marginBottom: '6px' }}>🤖 Android (Chrome / Edge / Samsung Internet):</div>
                <div style={{ fontSize: '0.85rem' }}>
                  1. Tap the browser menu (<strong>⋮</strong> three dots top-right).<br />
                  2. Tap <strong>"Install app"</strong> or <strong>"Add to Home screen"</strong>.<br />
                  3. Tap <strong>Install</strong> to add it to your apps list!
                </div>
              </div>

              <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
                <div style={{ fontWeight: 700, color: '#34d399', marginBottom: '6px' }}>🍏 Apple iOS (iPhone / iPad Safari):</div>
                <div style={{ fontSize: '0.85rem' }}>
                  1. Tap the <strong>Share</strong> button (square with arrow ⎋ at bottom).<br />
                  2. Scroll down and tap <strong>"Add to Home Screen"</strong> (➕).<br />
                  3. Tap <strong>Add</strong> top-right to launch it as a full-screen app!
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button className="action-btn" onClick={() => setShowInstallGuide(false)}>
                Got it
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Backend Server Connection & Diagnostics Modal */}
      {showServerConfigModal && (
        <div className="modal-backdrop" onClick={() => setShowServerConfigModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '520px' }}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '1.5rem' }}>🔌</span>
                <div>
                  <h3 style={{ margin: 0 }}>Backend Connection Diagnostics</h3>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Port 8000 & Cloud Tunnel Synchronization
                  </div>
                </div>
              </div>
              <button className="close-btn" onClick={() => setShowServerConfigModal(false)}>✕</button>
            </div>

            <div style={{ padding: '8px 0', fontSize: '0.88rem' }}>
              {/* Current Status Box */}
              <div style={{
                background: isApiOnline ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
                border: `1px solid ${isApiOnline ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                borderRadius: '8px',
                padding: '12px 14px',
                marginBottom: '16px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span className={`status-dot ${isApiOnline ? 'dot-online' : 'dot-offline'}`} />
                    <strong style={{ color: isApiOnline ? '#34d399' : '#f87171' }}>
                      {isApiOnline ? 'Backend Online & Synchronized' : 'Backend Disconnected'}
                    </strong>
                  </div>
                  {serverLatency && (
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                      {serverLatency}ms ping
                    </span>
                  )}
                </div>
                {serverHealth && (
                  <div style={{ marginTop: '8px', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                    Database: <span style={{ color: '#38bdf8' }}>{serverHealth.database}</span> &bull; Version: <span style={{ color: '#38bdf8' }}>{serverHealth.version}</span> &bull; Status: <span style={{ color: '#34d399' }}>{serverHealth.status}</span>
                  </div>
                )}
                {errorMsg && !isApiOnline && (
                  <div style={{ marginTop: '6px', fontSize: '0.75rem', color: '#fca5a5' }}>
                    {errorMsg}
                  </div>
                )}
              </div>

              {/* Target Server URL Input */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Active API Endpoint URL:
                </label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="text"
                    value={serverConfigInput}
                    onChange={(e) => setServerConfigInput(e.target.value)}
                    placeholder="https://.../api or http://192.168...:8000/api"
                    className="form-input"
                    style={{ flex: 1, fontFamily: 'monospace', fontSize: '0.82rem' }}
                  />
                  <button
                    className="action-btn"
                    onClick={() => handleTestAndApplyServer(serverConfigInput)}
                    disabled={testingConnection}
                    style={{ whiteSpace: 'nowrap' }}
                  >
                    {testingConnection ? 'Testing...' : '⚡ Test & Connect'}
                  </button>
                </div>
                {testResult && (
                  <div style={{
                    marginTop: '8px',
                    fontSize: '0.8rem',
                    color: testResult.success ? '#34d399' : '#f87171',
                    padding: '6px 10px',
                    borderRadius: '6px',
                    background: testResult.success ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)'
                  }}>
                    {testResult.message}
                  </div>
                )}
              </div>

              {/* Quick Preset Buttons */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  Quick Connection Presets:
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                  <button
                    type="button"
                    className="server-preset-btn"
                    onClick={() => {
                      setServerConfigInput('https://lucky-rings-strive.loca.lt/api');
                      handleTestAndApplyServer('https://lucky-rings-strive.loca.lt/api');
                    }}
                  >
                    <div style={{ fontWeight: 600, color: '#38bdf8' }}>🌐 Public Tunnel (Live)</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>lucky-rings-strive.loca.lt</div>
                  </button>

                  <button
                    type="button"
                    className="server-preset-btn"
                    onClick={() => {
                      setServerConfigInput('http://192.168.29.102:8000/api');
                      handleTestAndApplyServer('http://192.168.29.102:8000/api');
                    }}
                  >
                    <div style={{ fontWeight: 600, color: '#34d399' }}>📶 Local Wi-Fi</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>192.168.29.102:8000</div>
                  </button>

                  <button
                    type="button"
                    className="server-preset-btn"
                    onClick={() => {
                      setServerConfigInput('http://localhost:8000/api');
                      handleTestAndApplyServer('http://localhost:8000/api');
                    }}
                  >
                    <div style={{ fontWeight: 600, color: '#a78bfa' }}>💻 Local PC</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>localhost:8000</div>
                  </button>

                  <button
                    type="button"
                    className="server-preset-btn"
                    onClick={() => {
                      const auto = `${window.location.origin}/api`;
                      setServerConfigInput(auto);
                      handleTestAndApplyServer(auto);
                    }}
                  >
                    <div style={{ fontWeight: 600, color: '#f59e0b' }}>🔄 Auto-Detect</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Current Origin /api</div>
                  </button>
                </div>
              </div>

              {/* Mobile Help Note */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '10px 12px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                💡 <strong>Phone Connection Tip:</strong>
                <ul style={{ margin: '4px 0 0 16px', padding: 0 }}>
                  <li>On same Wi-Fi: Tap <strong>Local Wi-Fi</strong> for maximum speed.</li>
                  <li>On mobile data: Tap <strong>Public Tunnel</strong> to route via HTTPS.</li>
                </ul>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '12px' }}>
              <button className="action-btn" onClick={() => setShowServerConfigModal(false)}>
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
