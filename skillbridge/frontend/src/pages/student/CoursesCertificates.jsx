import { useMemo, useState } from "react";
import PageHeader from "../../components/PageHeader.jsx";
import Badge from "../../components/Badge.jsx";
import { ExternalLink, Filter } from "lucide-react";

const COURSES = [
  { provider: "Infosys Springboard", title: "Programming Fundamentals with Python", mode: "Free", skill: "Python", type: "Certificate", url: "https://infyspringboard.onwingspan.com/" },
  { provider: "Infosys Springboard", title: "Data Analytics Foundation", mode: "Free", skill: "Data Analytics", type: "Certificate", url: "https://infyspringboard.onwingspan.com/" },
  { provider: "IBM", title: "Introduction to Cloud Computing", mode: "Free", skill: "Cloud", type: "Certificate", url: "https://www.coursera.org/learn/introduction-to-cloud" },
  { provider: "IBM", title: "Data Analysis with Python", mode: "Paid", skill: "Python", type: "Professional Certificate", url: "https://www.coursera.org/learn/data-analysis-with-python" },
  { provider: "Coursera", title: "Google Data Analytics Professional Certificate", mode: "Paid", skill: "Data Analytics", type: "Professional Certificate", url: "https://www.coursera.org/professional-certificates/google-data-analytics" },
  { provider: "Coursera", title: "Python for Everybody", mode: "Free to audit", skill: "Python", type: "Certificate", url: "https://www.coursera.org/specializations/python" },
  { provider: "IBM", title: "AI Engineering Foundations", mode: "Paid", skill: "AI", type: "Professional Certificate", url: "https://www.coursera.org/professional-certificates/ibm-ai-engineering" },
  { provider: "Infosys Springboard", title: "Digital Skills: Employability", mode: "Free", skill: "Employability", type: "Certificate", url: "https://infyspringboard.onwingspan.com/" },
  { provider: "Infosys Springboard", title: "Java Programming", mode: "Free", skill: "Java", type: "Certificate", url: "https://infyspringboard.onwingspan.com/" },
  { provider: "Infosys Springboard", title: "Introduction to Artificial Intelligence", mode: "Free", skill: "AI", type: "Certificate", url: "https://infyspringboard.onwingspan.com/" },
  { provider: "Infosys Springboard", title: "Database Management Systems", mode: "Free", skill: "SQL", type: "Certificate", url: "https://infyspringboard.onwingspan.com/" },
  { provider: "IBM", title: "Cybersecurity Fundamentals", mode: "Free", skill: "Cybersecurity", type: "Certificate", url: "https://www.coursera.org/learn/cybersecurity-basics" },
  { provider: "IBM", title: "Python Project for Data Science", mode: "Paid", skill: "Python", type: "Professional Certificate", url: "https://www.coursera.org/learn/python-project-for-data-science" },
  { provider: "IBM", title: "DevOps and Software Engineering", mode: "Paid", skill: "DevOps", type: "Professional Certificate", url: "https://www.coursera.org/professional-certificates/devops-and-software-engineering" },
  { provider: "Coursera", title: "Meta Front-End Developer", mode: "Paid", skill: "Web Development", type: "Professional Certificate", url: "https://www.coursera.org/professional-certificates/meta-front-end-developer" },
  { provider: "Coursera", title: "Google IT Automation with Python", mode: "Paid", skill: "Python", type: "Professional Certificate", url: "https://www.coursera.org/professional-certificates/google-it-automation" },
  { provider: "Coursera", title: "Machine Learning Specialization", mode: "Free to audit", skill: "Machine Learning", type: "Certificate", url: "https://www.coursera.org/specializations/machine-learning-introduction" },
  { provider: "Coursera", title: "Excel Skills for Business", mode: "Free to audit", skill: "Excel", type: "Certificate", url: "https://www.coursera.org/specializations/excel" },
];

export default function CoursesCertificates() {
  const [provider, setProvider] = useState("All");
  const [mode, setMode] = useState("All");
  const filtered = useMemo(() => COURSES.filter((course) => (provider === "All" || course.provider === provider) && (mode === "All" || course.mode === mode)), [provider, mode]);

  return (
    <div>
      <PageHeader title="Courses & Certificates" subtitle="Choose learning by provider, cost, and the skills needed for your target role." />
      <div className="flex flex-wrap items-center gap-2 mb-5"><Filter size={16} className="text-slate-400" /><select value={provider} onChange={(e) => setProvider(e.target.value)} className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white"><option>All</option><option>Infosys Springboard</option><option>Coursera</option><option>IBM</option></select><select value={mode} onChange={(e) => setMode(e.target.value)} className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white"><option>All</option><option>Free</option><option>Free to audit</option><option>Paid</option></select></div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">{filtered.map((course) => <article key={course.title} className="bg-white border border-slate-200 rounded-xl p-4"><div className="flex items-start justify-between gap-3"><div><div className="text-xs text-brand-600 font-medium">{course.provider}</div><h2 className="text-sm font-semibold text-slate-800 mt-1">{course.title}</h2></div><Badge>{course.mode}</Badge></div><div className="flex items-center gap-2 mt-4"><span className="text-xs text-slate-500">Skill: {course.skill}</span><span className="text-xs text-slate-300">·</span><span className="text-xs text-slate-500">{course.type}</span></div><a href={course.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-xs text-brand-600 hover:underline mt-4">View course <ExternalLink size={13} /></a></article>)}</div>
      {filtered.length === 0 && <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-sm text-slate-500">No courses match these filters.</div>}
      <p className="text-[11px] text-slate-400 mt-5">Prices and availability can change on provider sites. Check the course page before enrolling.</p>
    </div>
  );
}
