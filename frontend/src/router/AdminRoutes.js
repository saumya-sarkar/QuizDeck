import AdminDashboard from "@/views/Admin/AdminDashboard.vue";
import Subjects from "@/views/Admin/Subjects.vue";
import Chapters from "@/views/Admin/Chapters.vue";
import Quizzes from "@/views/Admin/Quizzes.vue";
import Questions from "@/views/Admin/Questions.vue";
import AdminUsers from "@/views/Admin/AdminUsers.vue";
import CSVExportManager from "@/views/Admin/CSVExportManager.vue";
import AdminAnalytics from "@/views/Admin/AdminAnalytics.vue";
import QuizAttempts from "@/views/Admin/QuizAttempts.vue";
import AdminQuizResultPage from "@/views/Admin/AdminQuizResultPage.vue";

const AdminRoutes = [
  {
    path: "/admin",
    name: "AdminDashboard",
    component: AdminDashboard,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Admin Dashboard"
    },
  },
  {
    path: "/admin/subjects",
    name: "Subjects",
    component: Subjects,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Subjects"
    },
  },
  {
    path: "/admin/subjects/:subjectId/chapters",
    name: "Chapters",
    component: Chapters,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Chapters"
    },
  },
  {
    path: "/admin/subjects/:subjectId/chapters/:chapterId/quizzes",
    name: "Quizzes",
    component: Quizzes,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Quizzes"
    },
  },
  {
    path: "/admin/subjects/:subjectId/chapters/:chapterId/quizzes/:quizId/questions",
    name: "Questions",
    component: Questions,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Questions"
    },
  },
  {
    path: "/admin/users",
    name: "AdminUsers",
    component: AdminUsers,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "User Management"
    },
  },
  {
    path: "/admin/users/:currentUserId/attempts",
    name: "QuizAttempts",
    component: QuizAttempts,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Quiz Attempts"
    },
  },
  {
    path: "/admin/users/:currentUserId/attempts/:currentAttemptId",
    name: "AdminQuizResultPage",
    component: AdminQuizResultPage,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "Quiz Results"
    },
  },
  {
    path: "/admin/csv-export",
    name: "CSVExportManager", 
    component: CSVExportManager,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "CSV Export"
    },
  },
  {
  path: "/admin/analytics",
  name: "AdminAnalytics", 
  component: AdminAnalytics,
  meta: {
    requiresAuth: true,
    requiresAdmin: true,
    title: "Analytics Dashboard"
    },
  }
];

export default AdminRoutes;