import { useState } from "react";
import { UploadCloud } from "lucide-react";
import PageHeader from "../../components/PageHeader.jsx";
import api from "../../services/api.js";

export default function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.uploadResume(file);
      setResult(res);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not parse this resume.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-xl">
      <PageHeader title="Upload Resume" subtitle="We'll extract your skills automatically and merge them into your profile" />

      <div className="bg-white border-2 border-dashed border-slate-200 rounded-xl p-8 text-center">
        <UploadCloud className="mx-auto text-slate-300 mb-3" size={36} />
        <input
          type="file" accept=".pdf,.docx"
          onChange={(e) => setFile(e.target.files[0])}
          className="text-sm mx-auto"
        />
        <p className="text-xs text-slate-400 mt-2">PDF or DOCX only</p>
      </div>

      <button
        onClick={handleUpload} disabled={!file || uploading}
        className="mt-4 px-4 py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50"
      >
        {uploading ? "Parsing…" : "Upload & Parse"}
      </button>

      {error && <div className="text-sm text-red-600 mt-3">{error}</div>}

      {result && (
        <div className="mt-5 bg-white border border-slate-200 rounded-xl p-4">
          <div className="text-sm text-emerald-700 mb-2">{result.message}</div>
          <div className="flex flex-wrap gap-2">
            {result.extracted_skills.map((s) => (
              <span key={s} className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 text-xs">{s}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
