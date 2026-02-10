import React, { useEffect, useMemo, useState } from "react";

const backendUrl = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

// ============================================
// DAZZA — Elegant Dark Deepfake Detector UI
// ============================================

// Icon Components
const UploadIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
  </svg>
);

const SparkleIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
  </svg>
);

const LoadingSpinner = () => (
  <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

const ShieldIcon = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
  </svg>
);

export default function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${backendUrl}/metrics`);
        if (!res.ok) return;
        const data = await res.json();
        setMetrics(data);
      } catch (err) {
        console.warn("Metrics fetch failed", err);
      }
    })();
  }, [result]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError("Please choose an image first.");
      return;
    }
    setIsLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await fetch(`${backendUrl}/predict`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error(`Backend responded with ${response.status}`);
      }
      const payload = await response.json();
      setResult({
        ...payload,
        saliencyUrl: `${backendUrl}${payload.saliency_path}`,
      });
    } catch (err) {
      console.error(err);
      setError("Prediction failed. Ensure the backend service is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile && droppedFile.type.startsWith("image/")) {
      setFile(droppedFile);
      setResult(null);
      setError("");
    }
  };

  return (
    <>
      {/* Space Ambience Background */}
      <div className="space-bg" aria-hidden="true" />
      <div className="vignette" aria-hidden="true" />

      {/* Main Container */}
      <div className="relative min-h-screen">
        <div className="max-w-6xl mx-auto px-6 py-12 lg:py-16">
          
          {/* Header */}
          <header className="text-center mb-14 animate-in">
            <div className="inline-flex items-center gap-2 mb-6">
              <ShieldIcon className="w-10 h-10 text-accent-violet" />
              <h1 className="text-4xl lg:text-5xl font-bold tracking-tight text-gradient">
                Dazza
              </h1>
            </div>
            <p className="text-lg text-neutral-400 max-w-2xl mx-auto leading-relaxed">
              AI-powered deepfake detection with real-time analysis 
              <span className="text-neutral-500"> · </span>
              <span className="text-accent-violet/80">Grad-CAM explainability</span>
            </p>
          </header>

          {/* Upload Panel */}
          <form
            onSubmit={handleSubmit}
            className="glass-panel-elevated glow-effect p-8 mb-10 animate-in delay-100"
          >
            {/* Drag & Drop Zone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
                relative rounded-xl border-2 border-dashed p-8 mb-6 text-center
                transition-all duration-300 ease-out
                ${isDragOver 
                  ? "border-accent-violet bg-accent-glow" 
                  : "border-white/10 hover:border-white/20 hover:bg-white/[0.02]"
                }
              `}
            >
              <div className="flex flex-col items-center gap-4">
                <div className={`
                  p-4 rounded-2xl transition-all duration-300
                  ${isDragOver ? "bg-accent-violet/20" : "bg-white/[0.03]"}
                `}>
                  <UploadIcon />
                </div>
                <div>
                  <p className="text-neutral-300 font-medium mb-1">
                    Drop an image here, or{" "}
                    <label className="text-accent-violet hover:text-accent-purple cursor-pointer transition-colors">
                      browse
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(event) => {
                          setFile(event.target.files?.[0] ?? null);
                          setResult(null);
                          setError("");
                        }}
                        className="sr-only"
                      />
                    </label>
                  </p>
                  <p className="text-sm text-neutral-500">
                    Supports PNG, JPG, WebP up to 10MB
                  </p>
                </div>
              </div>

              {/* File Preview Badge */}
              {file && (
                <div className="mt-6 inline-flex items-center gap-3 px-4 py-2 rounded-xl bg-white/[0.05] border border-white/10">
                  <div className="w-10 h-10 rounded-lg overflow-hidden bg-void-800">
                    <img src={previewUrl} alt="" className="w-full h-full object-cover" />
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-medium text-neutral-200 truncate max-w-[200px]">
                      {file.name}
                    </p>
                    <p className="text-xs text-neutral-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => { setFile(null); setResult(null); }}
                    className="ml-2 p-1 rounded-lg hover:bg-white/10 text-neutral-400 hover:text-neutral-200 transition-colors"
                    aria-label="Remove file"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={!file || isLoading}
              className="btn-primary w-full focus-ring"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <SparkleIcon />
                  <span>Run Detection</span>
                </>
              )}
            </button>

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                <p className="text-sm text-red-400 flex items-center gap-2">
                  <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                  </svg>
                  {error}
                </p>
              </div>
            )}
          </form>

          {/* Results Section */}
          {result && (
            <section className="grid gap-6 lg:grid-cols-2 mb-10 animate-in delay-200">
              {/* Inference Results Card */}
              <article className="glass-panel p-6 glow-effect">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold text-neutral-100">Detection Result</h2>
                  <span className={result.label === "real" ? "badge-real" : "badge-deepfake"}>
                    {result.label}
                  </span>
                </div>
                
                {/* Confidence Meter */}
                <div className="mb-6">
                  <div className="flex justify-between items-baseline mb-2">
                    <span className="text-sm text-neutral-400">Confidence</span>
                    <span className="text-2xl font-bold text-gradient">
                      {(result.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-void-700 overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-700 ease-out"
                      style={{ 
                        width: `${result.confidence * 100}%`,
                        background: result.label === "real" 
                          ? "linear-gradient(90deg, #22c55e, #4ade80)" 
                          : "linear-gradient(90deg, #ef4444, #f87171)"
                      }}
                    />
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="stat-card">
                    <p className="stat-label">Inference Time</p>
                    <p className="stat-value">{result.inference_ms.toFixed(0)}<span className="text-sm text-neutral-500 ml-1">ms</span></p>
                  </div>
                  <div className="stat-card">
                    <p className="stat-label">Model Version</p>
                    <p className="stat-value text-base">v0.2.0</p>
                  </div>
                </div>
              </article>

              {/* Images Panel */}
              <article className="space-y-4">
                {previewUrl && (
                  <figure className="image-frame">
                    <span className="image-label">Original</span>
                    <img src={previewUrl} alt="Uploaded sample" />
                  </figure>
                )}
                <figure className="image-frame">
                  <span className="image-label">Grad-CAM Saliency</span>
                  <img src={result.saliencyUrl} alt="Saliency heatmap overlay" />
                </figure>
              </article>
            </section>
          )}

          {/* Metrics Section */}
          {metrics && (
            <section className="glass-panel p-6 animate-in delay-300">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-xl bg-accent-violet/10">
                  <svg className="w-5 h-5 text-accent-violet" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                  </svg>
                </div>
                <h2 className="text-lg font-semibold text-neutral-100">API Metrics</h2>
              </div>
              
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="stat-card">
                  <p className="stat-label">Total Predictions</p>
                  <p className="stat-value">{metrics.total_predictions.toLocaleString()}</p>
                </div>
                <div className="stat-card">
                  <p className="stat-label">Running Accuracy</p>
                  <p className="stat-value">{(metrics.running_accuracy * 100).toFixed(1)}%</p>
                </div>
                <div className="stat-card">
                  <p className="stat-label">Class Distribution</p>
                  <p className="stat-value text-base font-mono">
                    <span className="text-green-400">{metrics.class_counts?.real ?? 0}</span>
                    <span className="text-neutral-600 mx-2">/</span>
                    <span className="text-red-400">{metrics.class_counts?.deepfake ?? 0}</span>
                  </p>
                </div>
                <div className="stat-card">
                  <p className="stat-label">Last Updated</p>
                  <p className="stat-value text-base">
                    {new Date(metrics.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            </section>
          )}

          {/* Footer */}
          <footer className="mt-16 text-center animate-in delay-300">
            <p className="text-sm text-neutral-600">
              Built for responsible AI research
              <span className="mx-2">·</span>
              <a 
                href="https://github.com/eshan-159/DeepFake_Detector" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-neutral-500 hover:text-accent-violet transition-colors"
              >
                View on GitHub
              </a>
            </p>
          </footer>
        </div>
      </div>
    </>
  );
}
