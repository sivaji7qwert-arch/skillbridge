import { Routes, Route, Navigate } from "react-router-dom";
import PortalLayout from "./layouts/PortalLayout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";

// Student
import StudentOnboarding from "./pages/student/StudentOnboarding.jsx";
import StudentDashboard from "./pages/student/StudentDashboard.jsx";
import ResumeUpload from "./pages/student/ResumeUpload.jsx";
import CertificateUpload from "./pages/student/CertificateUpload.jsx";
import DsaPrep from "./pages/student/DsaPrep.jsx";
import JobBrowse from "./pages/student/JobBrowse.jsx";
import JobUp from "./pages/student/JobUp.jsx";
import InterviewPreparation from "./pages/student/InterviewPreparation.jsx";
import CoursesCertificates from "./pages/student/CoursesCertificates.jsx";

// Employer
import EmployerDashboard from "./pages/employer/EmployerDashboard.jsx";
import PostJob from "./pages/employer/PostJob.jsx";
import CandidateRanking from "./pages/employer/CandidateRanking.jsx";

// Institution
import InstitutionDashboard from "./pages/institution/InstitutionDashboard.jsx";
import InstitutionCourses from "./pages/institution/InstitutionCourses.jsx";

// Admin
import AdminDashboard from "./pages/admin/AdminDashboard.jsx";

// Shared labour-market analytics (visible to institution/admin via their own nav)
import LabourMarket from "./pages/LabourMarket.jsx";
import Skills from "./pages/Skills.jsx";
import JobRoles from "./pages/JobRoles.jsx";
import CurriculumAnalysis from "./pages/CurriculumAnalysis.jsx";
import ModelInsights from "./pages/ModelInsights.jsx";

import {
  LayoutDashboard, User, FileText, Award, Code2, Briefcase,
  Building2, Users as UsersIcon, GraduationCap, BookOpen,
  TrendingUp, Sparkles, GitCompareArrows, BrainCircuit, ArrowUp,
  MessageSquareText,
} from "lucide-react";

const STUDENT_NAV = [
  { to: "/student", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/student/onboarding", label: "Profile Setup", icon: User },
  { to: "/student/resume", label: "Resume Upload", icon: FileText },
  { to: "/student/certificates", label: "Certificates", icon: Award },
  { to: "/student/dsa", label: "DSA Prep", icon: Code2 },
  { to: "/student/jobs", label: "Browse Jobs", icon: Briefcase },
  { to: "/student/job-up", label: "Job Up", icon: ArrowUp },
  { to: "/student/interview-prep", label: "Interview Prep", icon: MessageSquareText },
  { to: "/student/courses", label: "Courses & Certificates", icon: GraduationCap },
];

const EMPLOYER_NAV = [
  { to: "/employer", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/employer/post-job", label: "Post a Job", icon: Briefcase },
  { to: "/employer/job-up", label: "Job Up", icon: ArrowUp },
  { to: "/employer/interview-prep", label: "Interview Prep", icon: MessageSquareText },
];

const INSTITUTION_NAV = [
  { to: "/institution", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/institution/courses", label: "Courses", icon: BookOpen },
  { to: "/institution/labour-market", label: "Labour Market", icon: TrendingUp },
  { to: "/institution/curriculum-analysis", label: "Skill Gap Analysis", icon: GitCompareArrows },
];

const ADMIN_NAV = [
  { to: "/admin", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/admin/skills", label: "Skills", icon: Sparkles },
  { to: "/admin/job-roles", label: "Job Roles", icon: Briefcase },
  { to: "/admin/model-insights", label: "Model Insights", icon: BrainCircuit },
];

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Student portal */}
      <Route
        element={
          <ProtectedRoute allowedRoles={["student"]}>
            <PortalLayout navItems={STUDENT_NAV} portalLabel="Student Portal" />
          </ProtectedRoute>
        }
      >
        <Route path="/student" element={<StudentDashboard />} />
        <Route path="/student/onboarding" element={<StudentOnboarding />} />
        <Route path="/student/resume" element={<ResumeUpload />} />
        <Route path="/student/certificates" element={<CertificateUpload />} />
        <Route path="/student/dsa" element={<DsaPrep />} />
        <Route path="/student/jobs" element={<JobBrowse />} />
        <Route path="/student/job-up" element={<JobUp />} />
        <Route path="/student/interview-prep" element={<InterviewPreparation />} />
        <Route path="/student/courses" element={<CoursesCertificates />} />
      </Route>

      {/* Employer portal */}
      <Route
        element={
          <ProtectedRoute allowedRoles={["employer"]}>
            <PortalLayout navItems={EMPLOYER_NAV} portalLabel="Employer Portal" />
          </ProtectedRoute>
        }
      >
        <Route path="/employer" element={<EmployerDashboard />} />
        <Route path="/employer/post-job" element={<PostJob />} />
        <Route path="/employer/job-up" element={<JobUp />} />
        <Route path="/employer/interview-prep" element={<InterviewPreparation />} />
        <Route path="/employer/jobs/:jobId/candidates" element={<CandidateRanking />} />
      </Route>

      {/* Institution portal */}
      <Route
        element={
          <ProtectedRoute allowedRoles={["institution"]}>
            <PortalLayout navItems={INSTITUTION_NAV} portalLabel="Institution Portal" />
          </ProtectedRoute>
        }
      >
        <Route path="/institution" element={<InstitutionDashboard />} />
        <Route path="/institution/courses" element={<InstitutionCourses />} />
        <Route path="/institution/labour-market" element={<LabourMarket />} />
        <Route path="/institution/curriculum-analysis" element={<CurriculumAnalysis />} />
      </Route>

      {/* Government / Admin portal */}
      <Route
        element={
          <ProtectedRoute allowedRoles={["admin"]}>
            <PortalLayout navItems={ADMIN_NAV} portalLabel="Government Portal" />
          </ProtectedRoute>
        }
      >
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/skills" element={<Skills />} />
        <Route path="/admin/job-roles" element={<JobRoles />} />
        <Route path="/admin/model-insights" element={<ModelInsights />} />
      </Route>
    </Routes>
  );
}
