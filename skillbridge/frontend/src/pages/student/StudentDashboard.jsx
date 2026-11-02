import { Link } from "react-router-dom";
import PageHeader from "../../components/PageHeader.jsx";
import Badge from "../../components/Badge.jsx";
import useFetch from "../../hooks/useFetch.js";
import api from "../../services/api.js";

export default function StudentDashboard() {
  const { data: profile, loading: profileLoading, error: profileError } = useFetch(() => api.getMyProfile(), []);
  const { data: gap, loading: gapLoading } = useFetch(() => api.getMySkillGap(), [profile]);
  const { data: courses, loading: coursesLoading } = useFetch(() => api.getMyCourseRecommendations(), [profile]);

  if (profileError?.response?.status === 404) {
    return (
      <div className="max-w-md mx-auto text-center py-16">
        <h2 className="text-lg font-semibold text-slate-900 mb-2">Complete your profile</h2>
        <p className="text-sm text-slate-500 mb-4">We need a few details to generate your skill-gap analysis.</p>
        <Link to="/student/onboarding" className="inline-block px-4 py-2 rounded-lg bg-brand-600 text-white text-sm font-medium">
          Start Onboarding
        </Link>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title={profile ? `Welcome, ${profile.full_name}` : "Dashboard"}
        subtitle={profile ? `${profile.course} · ${profile.branch} · Target: ${profile.target_role}` : ""}
      />

      {(profileLoading || gapLoading) && <div className="text-sm text-slate-400">Loading…</div>}

      {gap && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div>
            <div className="bg-white rounded-xl border border-slate-200 p-4 mb-4">
              <div className="text-xs text-slate-500">Skill Match for {gap.target_role}</div>
              <div className="text-3xl font-semibold text-slate-900 mt-1">{gap.match_pct}%</div>
            </div>

            <div className="text-sm font-medium text-slate-700 mb-2">Missing Skills</div>
            <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
              {gap.missing_skills.map((m) => (
                <div key={m.skill} className="flex items-center justify-between px-4 py-2.5">
                  <span className="text-sm text-slate-800">{m.skill}</span>
                  <Badge>{m.priority}</Badge>
                </div>
              ))}
              {gap.missing_skills.length === 0 && (
                <div className="px-4 py-6 text-xs text-slate-400 text-center">No gaps detected — you're fully matched!</div>
              )}
            </div>
          </div>

          <div>
            <div className="text-sm font-medium text-slate-700 mb-2">Recommended Courses</div>
            {coursesLoading && <div className="text-sm text-slate-400">Loading…</div>}
            <div className="space-y-2">
              {(courses || []).map((c, i) => (
                <a key={i} href={c.url} target="_blank" rel="noreferrer"
                  className="block bg-white rounded-xl border border-slate-200 p-3 hover:border-brand-300">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-800">{c.title}</span>
                    <span className="text-[11px] text-slate-400">{c.provider}</span>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">Covers: {c.covers_missing_skills.join(", ")}</div>
                </a>
              ))}
              {(courses || []).length === 0 && !coursesLoading && (
                <div className="text-xs text-slate-400">No specific course matches yet — check back after adding more skill gaps.</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
