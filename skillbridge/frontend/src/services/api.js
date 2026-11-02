import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE_URL });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("skillbridge_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("skillbridge_token");
      localStorage.removeItem("skillbridge_user");
      if (window.location.pathname !== "/login") window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const api = {
  // Auth
  register: (payload) => client.post("/api/auth/register", payload).then((r) => r.data),
  login: (email, password) => client.post("/api/auth/login", { email, password }).then((r) => r.data),
  me: () => client.get("/api/auth/me").then((r) => r.data),

  // Student portal
  completeOnboarding: (payload) => client.post("/api/students/onboarding", payload).then((r) => r.data),
  getMyProfile: () => client.get("/api/students/me/profile").then((r) => r.data),
  getMySkillGap: () => client.get("/api/students/me/skill-gap").then((r) => r.data),
  getMyCourseRecommendations: () => client.get("/api/students/me/course-recommendations").then((r) => r.data),
  getDsaRoadmap: () => client.get("/api/students/me/dsa-roadmap").then((r) => r.data),
  getDsaProgress: () => client.get("/api/students/me/dsa-progress").then((r) => r.data),
  getDsaNext: () => client.get("/api/students/me/dsa-next").then((r) => r.data),
  markDsaSolved: (payload) => client.post("/api/students/me/dsa-solve", payload).then((r) => r.data),

  uploadResume: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return client.post("/api/resumes/upload", formData, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r.data);
  },
  getMyResumes: () => client.get("/api/resumes/mine").then((r) => r.data),

  uploadCertificate: (file, certificateType = "Degree") => {
    const formData = new FormData();
    formData.append("file", file);
    return client.post(`/api/certificates/upload?certificate_type=${encodeURIComponent(certificateType)}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
  getMyCertificates: () => client.get("/api/certificates/mine").then((r) => r.data),

  browseJobs: (params) => client.get("/api/jobs", { params }).then((r) => r.data),
  applyToJob: (jobId) => client.post(`/api/jobs/${jobId}/apply`).then((r) => r.data),

  // Employer portal
  createOrUpdateCompany: (payload) => client.post("/api/employer/company", payload).then((r) => r.data),
  postJob: (payload) => client.post("/api/employer/jobs", payload).then((r) => r.data),
  getMyJobs: () => client.get("/api/employer/jobs").then((r) => r.data),
  getRankedCandidates: (jobId, params) => client.get(`/api/employer/jobs/${jobId}/candidates`, { params }).then((r) => r.data),
  getEmployerApplications: () => client.get("/api/employer/applications").then((r) => r.data),
  updateApplicationStatus: (applicationId, status) =>
    client.patch(`/api/employer/applications/${applicationId}`, { status }).then((r) => r.data),
  reviewCertificate: (certId, payload) => client.patch(`/api/certificates/${certId}/review`, payload).then((r) => r.data),

  // Institution portal
  addInstitutionCourse: (payload) => client.post("/api/institution/courses", payload).then((r) => r.data),
  getInstitutionCourses: () => client.get("/api/institution/courses").then((r) => r.data),
  getStudentSkillStats: () => client.get("/api/institution/student-skill-stats").then((r) => r.data),
  getPlacementReadiness: () => client.get("/api/institution/placement-readiness").then((r) => r.data),

  // Admin / government portal
  getAdminOverview: () => client.get("/api/admin/overview").then((r) => r.data),
  getDistrictSkillGaps: () => client.get("/api/admin/district-skill-gaps").then((r) => r.data),
  getInstitutionReadiness: () => client.get("/api/admin/institution-readiness").then((r) => r.data),
  getAdminEmergingRoles: () => client.get("/api/admin/emerging-roles").then((r) => r.data),

  // Labour-market analytics (shared across portals)
  getDashboard: () => client.get("/api/dashboard").then((r) => r.data),
  getLabourMarketOverview: () => client.get("/api/labour-market/overview").then((r) => r.data),
  getSkills: () => client.get("/api/skills").then((r) => r.data),
  getTrendingSkills: (limit = 10) => client.get("/api/skills/trending", { params: { limit } }).then((r) => r.data),
  getSkillsByCity: (city) => client.get("/api/skills/by-city", { params: { city } }).then((r) => r.data),
  getRoles: () => client.get("/api/roles").then((r) => r.data),
  getTrendingRoles: (limit = 10) => client.get("/api/roles/trending", { params: { limit } }).then((r) => r.data),
  getCurricula: () => client.get("/api/curriculum").then((r) => r.data),
  analyzeCurriculum: (role, curriculumId) =>
    client.post("/api/curriculum/analyze", { role, curriculum_id: curriculumId }).then((r) => r.data),
  getModelMetrics: () => client.get("/api/ml/metrics").then((r) => r.data),
  predictTrend: (features) => client.post("/api/ml/predict-trend", features).then((r) => r.data),
};

export default api;
