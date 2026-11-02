import { useState } from "react";
import PageHeader from "../../components/PageHeader.jsx";
import Badge from "../../components/Badge.jsx";
import { ArrowUpRight, Building2, CheckCircle2, Target, TrendingUp } from "lucide-react";

const TARGETS = {
  "Data Analyst": {
    package: "₹6–12 LPA",
    companies: ["Infosys", "IBM", "Accenture", "Deloitte"],
    skills: ["SQL", "Power BI", "Python", "Statistics"],
  },
  "Software Engineer": {
    package: "₹8–18 LPA",
    companies: ["IBM", "Infosys", "Microsoft", "TCS Digital"],
    skills: ["DSA", "Python", "SQL", "System Design"],
  },
  "Cloud Engineer": {
    package: "₹9–20 LPA",
    companies: ["IBM", "Infosys", "Accenture", "AWS Partners"],
    skills: ["AWS", "Docker", "Linux", "Terraform"],
  },
};

export default function JobUp() {
  const [target, setTarget] = useState("Data Analyst");
  const plan = TARGETS[target];

  return (
    <div>
      <PageHeader title="Job Up" subtitle="Build the skills and evidence that move you toward stronger roles and packages." />
      <div className="bg-brand-900 text-white rounded-xl p-5 mb-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <div className="text-xs text-brand-100/70 uppercase tracking-wide">Your next target</div>
            <h2 className="text-2xl font-semibold mt-1">{target}</h2>
            <div className="text-brand-100 mt-1">Typical package range: {plan.package}</div>
          </div>
          <select value={target} onChange={(e) => setTarget(e.target.value)} className="bg-white text-slate-800 rounded-lg px-3 py-2 text-sm">
            {Object.keys(TARGETS).map((role) => <option key={role}>{role}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <TrendingUp className="text-emerald-600" size={20} />
          <div className="text-xs text-slate-500 mt-3">Package opportunity</div>
          <div className="text-xl font-semibold text-slate-900 mt-1">Higher-growth roles</div>
          <p className="text-xs text-slate-500 mt-1">Prioritize skills with strong current demand.</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <Target className="text-brand-600" size={20} />
          <div className="text-xs text-slate-500 mt-3">Skill focus</div>
          <div className="flex flex-wrap gap-1.5 mt-2">{plan.skills.map((skill) => <Badge key={skill}>{skill}</Badge>)}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <Building2 className="text-orange-500" size={20} />
          <div className="text-xs text-slate-500 mt-3">Companies to target</div>
          <div className="text-sm font-medium text-slate-800 mt-1">{plan.companies.join(" · ")}</div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-slate-800">90-day upgrade plan</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          {["Master the core skills", "Build one proof project", "Practice and apply"].map((step, index) => (
            <div key={step} className="border-l-2 border-brand-500 pl-3">
              <div className="text-xs text-brand-600">Phase {index + 1}</div>
              <div className="text-sm font-medium text-slate-800 mt-1">{step}</div>
              <div className="text-xs text-slate-500 mt-1">{index === 0 ? plan.skills.slice(0, 2).join(" and ") : index === 1 ? "Publish a measurable portfolio project" : "Complete mock interviews and targeted applications"}</div>
            </div>
          ))}
        </div>
        <div className="mt-5 flex items-center gap-2 text-xs text-emerald-700"><CheckCircle2 size={15} /> Track progress from Interview Preparation and Courses.</div>
        <a href="https://www.linkedin.com/jobs/" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-sm text-brand-600 hover:underline mt-4">Explore current openings <ArrowUpRight size={14} /></a>
      </div>
    </div>
  );
}
