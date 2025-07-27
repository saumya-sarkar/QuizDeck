import AdminDashboard from "@/views/Admin/AdminDashboard.vue";
import Subjects from "@/views/Admin/Subjects.vue";
import Chapters from "@/views/Admin/Chapters.vue";
import Quizzes from "@/views/Admin/Quizzes.vue";
import Questions from "@/views/Admin/Questions.vue";
import AdminUsers from "@/views/Admin/AdminUsers.vue";
import CSVExportManager from "@/views/Admin/CSVExportManager.vue";


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
    path: "/admin/csv-export",
    name: "CSVExportManager", 
    component: CSVExportManager,
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
      title: "CSV Export"
    },
  }
//   {
//     path: "/admin/users",
//     name: "Users",
//     component: Users,
//     meta: {
//       requiresAuth: true,
//       title: "Users",
//       roles: ["admin"],
//     },
//   },
//   {
//     path: "/admin/transactions",
//     name: "Transactions",
//     component: Transactions,
//     meta: {
//       requiresAuth: true,
//       title: "Transactions",
//       roles: ["admin"],
//     },
//   },

//   {
//     path: "/admin/subject/:subjectId/chapter/:chapterId/quiz/create",
//     name: "CreateQuiz",
//     component: CreateQuiz,
//     meta: {
//       requiresAuth: true,
//       title: "Create Quiz",
//       roles: ["admin"],
//     },
//   },
//   {
//     path: "/admin/subject/:subjectId/chapter/:chapterId/quiz/:quizId",
//     name: "Quiz",
//     component: Quiz,
//     meta: {
//       requiresAuth: true,
//       title: "Quiz",
//       roles: ["admin"],
//     },
//   },
//   {
//     path: "/admin/subject/:subjectId/chapter/:chapterId/quiz/:quizId/edit",
//     name: "EditQuiz",
//     component: EditQuiz,
//     meta: {
//       requiresAuth: true,
//       title: "Edit Quiz",
//       roles: ["admin"],
//     },
//   },
//   {
//     path: "/admin/student/:id",
//     name: "StudentDetails",
//     component: StudentDetails,
//     meta: {
//       requiresAuth: true,
//       title: "Student Details",
//       roles: ["admin"],
//     },
//   },
//   {
//     path: "/admin/summary",
//     name: "Summary",
//     component: Summary,
//     meta: {
//       requiresAuth: true,
//       title: "Summary",
//       roles: ["admin"],
//     },
//   },
//   {
//     path: "/admin/student/:id/quizDetails/:quizId",
//     name: "user-quiz-details",
//     component: UserQuizDetails,
//     meta: {
//       requiresAuth: true,
//       title: "User Quiz Details",
//       roles: ["admin"],
//     },
//   },
];

export default AdminRoutes;