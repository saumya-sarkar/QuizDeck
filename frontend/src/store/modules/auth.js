import axios from 'axios';
import router from '@/router';

export default {
  namespaced: true,
  state: () => ({
    user: null
  }),
  mutations: {
    setUser(state, user) {
      state.user = user;
    },
    clearUser(state) {
      state.user = null;
    }
  },
  actions: {
    async userDetails(context) {
      const token = sessionStorage.getItem("access_token");
      if (!token) {
        const requiresAuth = router.currentRoute.value.matched.some(record => record.meta.requiresAuth);

        if (requiresAuth) {
          context.dispatch("logoutUser");
        }
      return;
      }

      try {
        const response = await axios.get("http://127.0.0.1:5000/api/user-details", {
          headers: {
            Authorization: `${token}`
          }
        });
        context.commit("setUser", response.data);
      } catch (error) {
        console.error("Error fetching user from token:", error);
        context.dispatch("logoutUser"); // Redirect to login if token is invalid
      }
    },
    async logoutUser(context) {
      sessionStorage.removeItem("access_token");
      context.commit("clearUser");
      router.push("/login");
    }
  },
  getters: {
    isAuthenticated: (state) => !!state.user,
    isAdmin: (state) => state.user?.roles?.includes('admin') || false,
    getUser: (state) => state.user
  }
};
