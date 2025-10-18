import React, { useEffect, useMemo, useState } from "react";

const backendUrl = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

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

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-5xl mx-auto px-4 py-10">
        <header className="text-center mb-10">
          <h1 className="text-3xl font-semibold">Deepfake Detector</h1>
          <p className="text-slate-400 mt-2">
            Upload a face image to receive a real vs deepfake prediction and Grad-CAM saliency overlay.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg grid gap-4"
        >
          <label className="block">
            <span className="text-sm uppercase tracking-wide text-slate-500">Choose image</span>
            <input
              type="file"
              accept="image/*"
              onChange={(event) => {
                setFile(event.target.files?.[0] ?? null);
                setResult(null);
                setError("");
              }}
              className="mt-2 block w-full text-sm text-slate-200 file:mr-4 file:rounded-md file:border-0 file:bg-indigo-600 file:px-4 file:py-2 file:text-sm file:font-semibold hover:file:bg-indigo-500"
            />
          </label>

          <button
            type="submit"
            disabled={!file || isLoading}
            className="inline-flex items-center justify-center rounded-md bg-indigo-600 px-4 py-2 font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? "Analyzing..." : "Run prediction"}
          </button>

          {error && <p className="text-sm text-red-400">{error}</p>}
        </form>

        {result && (
          <section className="mt-10 grid gap-6 lg:grid-cols-2">
            <article className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
              <h2 className="text-xl font-semibold">Inference Result</h2>
              <dl className="mt-4 space-y-2 text-sm text-slate-300">
                <div className="flex justify-between">
                  <dt>Label</dt>
                  <dd className="font-medium text-indigo-400 uppercase">{result.label}</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Confidence</dt>
                  <dd>{(result.confidence * 100).toFixed(2)}%</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Latency</dt>
                  <dd>{result.inference_ms.toFixed(1)} ms</dd>
                </div>
              </dl>
            </article>

            <article className="grid gap-4">
              {previewUrl && (
                <figure className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                  <figcaption className="px-4 py-2 text-sm text-slate-400">Original</figcaption>
                  <img src={previewUrl} alt="Uploaded sample" className="w-full" />
                </figure>
              )}
              <figure className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <figcaption className="px-4 py-2 text-sm text-slate-400">Saliency overlay</figcaption>
                <img src={result.saliencyUrl} alt="Saliency heatmap" className="w-full" />
              </figure>
            </article>
          </section>
        )}

        {metrics && (
          <section className="mt-12 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-lg font-semibold">API Metrics</h2>
            <dl className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-slate-300">
              <div>
                <dt className="uppercase text-xs text-slate-500">Total predictions</dt>
                <dd className="text-lg font-semibold">{metrics.total_predictions}</dd>
              </div>
              <div>
                <dt className="uppercase text-xs text-slate-500">Running accuracy</dt>
                <dd className="text-lg font-semibold">{(metrics.running_accuracy * 100).toFixed(1)}%</dd>
              </div>
              <div>
                <dt className="uppercase text-xs text-slate-500">Class counts</dt>
                <dd className="font-mono">
                  real: {metrics.class_counts?.real ?? 0} · fake: {metrics.class_counts?.deepfake ?? 0}
                </dd>
              </div>
              <div>
                <dt className="uppercase text-xs text-slate-500">Last update</dt>
                <dd>{new Date(metrics.updated_at).toLocaleString()}</dd>
              </div>
            </dl>
          </section>
        )}
      </div>
    </div>
  );
}
