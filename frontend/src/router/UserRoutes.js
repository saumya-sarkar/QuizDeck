import store from "@/store";
import UserDashboard from "../views/User/UserDashboard.vue";
import UserQuizAttempts from "../views/User/UserQuizAttempts.vue";
import UserSubjects from "../views/User/UserSubjects.vue";
import UserChapters from "../views/User/UserChapters.vue";
import UserQuizzes from "@/views/User/UserQuizzes.vue";
import QuizTaking from "@/views/User/QuizTaking.vue";
import QuizResultPage from "../views/User/QuizResultPage.vue";
import UserAnalytics from "@/views/User/UserAnalytics.vue";


const UserRoutes = [
    {
    path: "/user/:userId",
    name: "UserDashboard",
    component: UserDashboard,
    meta: {
      requiresAuth: true,
      title: "Dashboard"
    }
    },
    {
      path: "/user/:userId/subjects",
      name: "UserSubjects",
      component: UserSubjects,
      meta: {
        requiresAuth: true,
        title: "UserSubjects"
      },
    },
    {
        path: "/user/:userId/subjects/:subjectId/chapters",
        name: "UserChapters",
        component: UserChapters,
        meta: {
          requiresAuth: true,
          title: "UserChapters"
        },
      },
      {
          path: "/user/:userId/subjects/:subjectId/chapters/:chapterId/quizzes",
          name: "UserQuizzes",
          component: UserQuizzes,
          meta: {
            requiresAuth: true,
            title: "UserQuizzes"
          },
        },
        {
          path: '/user/:userId/quiz/:quizId/take',
          name: 'QuizTaking',
          component: QuizTaking,
          meta: {
            requiresAuth: true,
            title: 'Taking Quiz'
          },
          beforeEnter: (to, from, next) => {
            // Optional: Add any pre-route validation here
            next();
          }
        },
        {
          path: `/user/:userId/quiz-attempts`,
          name: "UserQuizAttempts",
          component: UserQuizAttempts,
          meta: {
            requiresAuth: true,
            title: "Quiz Attempts"
          }
        },
        {
          path: `/user/:userId/quiz/:quizId/result/:attemptId`,
          name: "QuizResultPage",
          component: QuizResultPage,
          meta: {
            requiresAuth: true,
            title: "Quiz Result"
          }
    },
    {
    path: `/user/:userId/analytics`,
    name: "UserAnalytics",
    component: UserAnalytics,
    meta: {
      requiresAuth: true,
      title: "My Analytics"
    }
    }
];

export default UserRoutes;