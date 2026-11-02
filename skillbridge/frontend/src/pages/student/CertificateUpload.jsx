import { useState } from "react";
import { UploadCloud } from "lucide-react";
import PageHeader from "../../components/PageHeader.jsx";
import Badge from "../../components/Badge.jsx";
import useFetch from "../../hooks/useFetch.js";
import api from "../../services/api.js";

const RECOMMENDED_CERTIFICATIONS = [
  { provider: "Infosys Springboard", title: "Programming Fundamentals with Python", mode: "Free", url: "https://infyspringboard.onwingspan.com/" },
  { provider: "Infosys Springboard", title: "Digital Skills: Employability", mode: "Free", url: "https://infyspringboard.onwingspan.com/" },
  { provider: "IBM", title: "IBM Data Analyst Professional Certificate", mode: "Paid", url: "https://www.coursera.org/professional-certificates/ibm-data-analyst" },
  { provider: "IBM", title: "IBM Cybersecurity Analyst Professional Certificate", mode: "Paid", url: "https://www.coursera.org/professional-certificates/ibm-cybersecurity-analyst" },
  { provider: "Coursera", title: "Google Data Analytics Professional Certificate", mode: "Paid", url: "https://www.coursera.org/professional-certificates/google-data-analytics" },
  { provider: "Coursera", title: "Python for Everybody", mode: "Free to audit", url: "https://www.coursera.org/specializations/python" },
];

export default function CertificateUpload() {
  const [file, setFile] = useState(null);
  const [certType, setCertType] = useState("Degree");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const { data: certificates, loading } = useFetch(() => api.getMyCertificates(), [refreshKey]);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.uploadCertificate(file, certType);
      setResult(res);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not upload this certificate.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-xl">
      <PageHeader title="Certificates" subtitle="Upload degree or course certificates for institution/employer verification" />

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800 mb-4">
        Uploading extracts readable text via OCR for a reviewer's convenience — it does not automatically verify
        authenticity. A human reviewer must confirm before status becomes "Verified."
      </div>

      <div className="bg-white border-2 border-dashed border-slate-200 rounded-xl p-6 text-center">
        <UploadCloud className="mx-auto text-slate-300 mb-3" size={32} />
        <select value={certType} onChange={(e) => setCertType(e.target.value)}
          className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm mb-3">
          <option>Degree</option>
          <option>Course Completion</option>
          <option>Other</option>
        </select>
        <br />
        <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={(e) => setFile(e.target.files[0])} className="text-sm" />
      </div>

      <button onClick={handleUpload} disabled={!file || uploading}
        className="mt-4 px-4 py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 disabled:opacity-50">
        {uploading ? "Uploading…" : "Upload"}
      </button>

      {error && <div className="text-sm text-red-600 mt-3">{error}</div>}
      {result && <div className="text-sm text-emerald-700 mt-3">Uploaded. Status: {result.status}</div>}

      <div className="mt-6">
        <div className="text-sm font-medium text-slate-700 mb-2">Your Certificates</div>
        {loading && <div className="text-sm text-slate-400">Loading…</div>}
        <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
          {(certificates || []).map((c) => (
            <div key={c.certificate_id} className="flex items-center justify-between px-4 py-2.5">
              <span className="text-sm text-slate-700">{c.certificate_type}</span>
              <Badge>{c.status}</Badge>
            </div>
          ))}
          {(certificates || []).length === 0 && !loading && (
            <div className="px-4 py-6 text-xs text-slate-400 text-center">No certificates uploaded yet.</div>
          )}
        </div>
      </div>

      <div className="mt-8">
        <div className="text-sm font-medium text-slate-700 mb-2">Recommended Certifications</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {RECOMMENDED_CERTIFICATIONS.map((certificate) => (
            <a key={certificate.title} href={certificate.url} target="_blank" rel="noreferrer"
              className="bg-white border border-slate-200 rounded-xl p-4 hover:border-brand-300">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs text-brand-600">{certificate.provider}</div>
                  <div className="text-sm font-medium text-slate-800 mt-1">{certificate.title}</div>
                </div>
                <Badge>{certificate.mode}</Badge>
              </div>
              <div className="text-xs text-brand-600 mt-3">View certification <span aria-hidden="true">↗</span></div>
            </a>
          ))}
        </div>
        <p className="text-[11px] text-slate-400 mt-3">Provider pricing and certificate eligibility may change. Verify details before enrolling.</p>
      </div>
    </div>
  );
}
