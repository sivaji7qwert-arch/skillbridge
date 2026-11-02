import { useState } from "react";
import PageHeader from "../components/PageHeader.jsx";
import Badge from "../components/Badge.jsx";
import useFetch from "../hooks/useFetch.js";
import api from "../services/api.js";

const DEFAULT_FEATURES = {
  demand_percentage: 20,
  growth_pct: 30,
  recent_count: 100,
  prior_count: 70,
  avg_salary: 900000,
  salary_score: 60,
  geo_avg_demand_pct: 25,
  frequency_score: 55,
  growth_score: 65,
  geo_score: 50,
};

export default function ModelInsights() {
  const { data: metrics, loading, error } = useFetch(() => api.getModelMetrics(), []);
  const [features, setFeatures] = useState(DEFAULT_FEATURES);
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);

  const runPrediction = async () => {
    setPredicting(true);
    try {
      const res = await api.predictTrend(features);
      setPrediction(res);
    } catch {
      setPrediction(null);
    } finally {
      setPredicting(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Model Insights"
        subtitle="The trained RandomForest classifier behind trend detection — held-out test performance and a live prediction sandbox"
      />

      {loading && <div className="text-sm text-slate-400">Loading model metrics…</div>}
      {error && (
        <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
          No trained model found yet. Run <code className="bg-white px-1 rounded">python scripts/train_model.py</code> from the backend, then reload.
        </div>
      )}

      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="text-xs text-slate-500 mb-2">Trend Classifier — held-out test accuracy</div>
            <div className="text-3xl font-semibold text-slate-900">
              {metrics.classifier ? `${(metrics.classifier.accuracy * 100).toFixed(1)}%` : "—"}
            </div>
            {metrics.classifier && (
              <div className="mt-3 space-y-1">
                {Object.entries(metrics.classifier.feature_importance)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 5)
                  .map(([feat, imp]) => (
                    <div key={feat} className="flex items-center gap-2 text-xs">
                      <span className="w-32 text-slate-500 truncate">{feat}</span>
                      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-brand-500" style={{ width: `${imp * 100 * 3}%` }} />
                      </div>
                      <span className="text-slate-400 w-10 text-right">{(imp * 100).toFixed(1)}%</span>
                    </div>
                  ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="text-xs text-slate-500 mb-2">Demand Score Regressor — mean absolute error</div>
            <div className="text-3xl font-semibold text-slate-900">
              {metrics.regressor ? `±${metrics.regressor.mae}` : "—"}
              <span className="text-sm text-slate-400 font-normal ml-1">points (0–100 scale)</span>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 p-4">
        <div className="text-sm font-medium text-slate-700 mb-3">Try a Prediction</div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-3">
          {Object.keys(DEFAULT_FEATURES).map((key) => (
            <div key={key}>
              <label className="block text-[11px] text-slate-400 mb-1">{key}</label>
              <input
                type="number"
                value={features[key]}
                onChange={(e) => setFeatures({ ...features, [key]: parseFloat(e.target.value) || 0 })}
                className="w-full border border-slate-200 rounded-lg px-2 py-1 text-xs"
              />
            </div>
          ))}
        </div>
        <button
          onClick={runPrediction}
          disabled={predicting}
          className="px-4 py-1.5 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50"
        >
          {predicting ? "Predicting…" : "Predict Trend"}
        </button>

        {prediction && (
          <div className="mt-4 flex items-center gap-3">
            <span className="text-sm text-slate-600">Predicted:</span>
            <Badge>{prediction.predicted_trend}</Badge>
            <div className="flex gap-2 text-xs text-slate-400">
              {Object.entries(prediction.class_probabilities).map(([cls, p]) => (
                <span key={cls}>{cls}: {(p * 100).toFixed(0)}%</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
