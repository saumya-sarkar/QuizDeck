// import { useQuizStore } from "../stores/quizStore";
// import { useQuizResultStore } from "../stores/quizResultStore";
// import StudentLayout from "../views/Student/StudentLayout.vue";
import store from "@/store";
import UserDashboard from "../views/User/UserDashboard.vue";
import UserQuizAttempts from "../views/User/UserQuizAttempts.vue";
import UserSubjects from "../views/User/UserSubjects.vue";
import UserChapters from "../views/User/UserChapters.vue";
import UserQuizzes from "@/views/User/UserQuizzes.vue";
import QuizTaking from "@/views/User/QuizTaking.vue";
import QuizResultPage from "../views/User/QuizResultPage.vue";
import UserAnalytics from "@/views/User/UserAnalytics.vue";
// import Subject from "../views/Student/Subject.vue";
// const QuizDetails = () =>
//   import(/*{ webpackPrefetch: true }*/ "../views/Student/Quiz.vue");
// const QuizTaking = () =>
//   import(/*{ webpackPrefetch: true }*/ "../views/Student/QuizTaking.vue");
// const QuizResults = () =>
//   import(/*{ webpackPrefetch: true }*/ "../views/Student/QuizResults.vue");
// const Quizzes = () =>
//   import(/*{ webpackPrefetch: true }*/ "../views/Student/Quizzes.vue");
// const DetailedPerformance = () =>
//   import("../views/Student/DetailedPerformance.vue");
// const Summary = () =>
//   import(/*{ webpackPrefetch: true }*/ "../views/Student/Summary.vue");
// const Transactions = () =>
//   import(/*{ webpackPrefetch: true }*/ "../views/Student/Transactions.vue");


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
  },
//       {
//         path: "quiz/history",
//         name: "quiz-history",
//         component: DetailedPerformance,
//         meta: {
//           requiresAuth: true,
//           title: "Quiz History",
//         },
//       },
//       {
//         path: "summary",
//         name: "summary",
//         component: Summary,
//         meta: {
//           requiresAuth: true,
//           title: "Summary",
//         },
//       },
//       {
//         path: "transactions",
//         name: "transactions",
//         component: Transactions,
//         meta: {
//           requiresAuth: true,
//           title: "Transactions",
//         },
//       },
//       {
//         path: "quiz/:quizId/results",
//         name: "quiz-results",
//         component: QuizResults,
//         meta: {
//           requiresAuth: true,
//           title: "Quiz Results",
//         },
//       },
//     ],
//   },
//   {
//     path: "/student/:id/subject/:subjectId/chapter/:chapterId/quiz/:quizId/take",
//     name: "quiz-take",
//     component: QuizTaking,
//     meta: {
//       requiresAuth: true,
//       title: "Taking Quiz",
//       roles: ["student"],
//       preventRefresh: true, // to handle refresh warnings
//     },
//     beforeEnter: async (to, from, next) => {
//       const quizStore = useQuizStore();

//       try {
//         // Check if quiz is in progress
//         const quizStartTime = localStorage.getItem("quizStartTime");
//         const isInProgress =
//           quizStartTime && (await quizStore.checkQuizStatus(to.params.quizId));

//         if (!isInProgress && from.name !== "quiz") {
//           // If quiz is not in progress and not coming from quiz details page
//           next({
//             name: "quiz",
//             params: {
//               id: to.params.id,
//               quizId: to.params.quizId,
//             },
//           });
//           return;
//         }

//         next();
//       } catch (error) {
//         console.error("Error checking quiz status:", error);
//         next({ name: "error" });
//       }
//     },
//   },
];

// const addNavigationGuards = (router) => {
//   // Clean up when leaving quiz-related routes
//   router.afterEach((to, from) => {
//     if (from.name === "quiz-take" && to.name !== "quiz-results") {
//       // Clear quiz data if leaving quiz without completing
//       localStorage.removeItem("quizStartTime");
//       localStorage.removeItem("totalDuration");
//       const quizStore = useQuizStore();
//       quizStore.resetQuiz();
//     }
//   });
// };

// export { UserRoutes, addNavigationGuards };

export default UserRoutes;