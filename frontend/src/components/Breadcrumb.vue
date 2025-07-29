<template>
  <nav aria-label="breadcrumb" class="breadcrumb-container">
    <ol class="breadcrumb glass-breadcrumb">
      <li 
        v-for="(item, index) in breadcrumbItems" 
        :key="index"
        class="breadcrumb-item"
        :class="{ active: index === breadcrumbItems.length - 1 }"
      >
        <router-link 
          v-if="item.path && index < breadcrumbItems.length - 1"
          v-bind:to="item.path"
          class="breadcrumb-link"
        >
          <font-awesome-icon 
            v-if="item.icon" 
            v-bind:icon="item.icon" 
            class="me-2" 
          />
          {{ item.name }}
        </router-link>
        <span v-else class="breadcrumb-current">
          <font-awesome-icon 
            v-if="item.icon" 
            :icon="item.icon" 
            class="me-2" 
          />
          {{ item.name }}
        </span>
      </li>
    </ol>
  </nav>
</template>

<script>
export default {
  name: 'Breadcrumb',
  props: {
    items: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  computed: {
    breadcrumbItems() {
      const isAdmin = this.$store.getters['auth/isAdmin'];
      if (isAdmin){
        // Always start with Dashboard as the root
        const baseItems = [
          {
            name: 'Dashboard',
            path: '/admin',
            icon: 'table-columns'
          }
        ];
      
        // Add the provided items
        return [...baseItems, ...this.items];
      } else if (!isAdmin){
        const userId = this.$store.getters['auth/getUser'].id;
        // Always start with Dashboard as the root
        const baseItems = [
        {
          name: 'Dashboard',
          path: `/user/${userId}`,
          icon: 'table-columns'
        }
        ];
      
        // Add the provided items
        return [...baseItems, ...this.items];
      }
      
    }
  }
};
</script>

<style scoped>
.breadcrumb-container {
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}

.glass-breadcrumb {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  padding: 0.75rem 1.5rem;
  margin-bottom: 0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.breadcrumb-item {
  font-size: 0.9rem;
  font-weight: 500;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: "›";
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  font-size: 1.1rem;
  margin: 0 0.5rem;
}

.breadcrumb-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  transition: all 0.3s ease;
  padding: 0.25rem 0.5rem;
  border-radius: 15px;
  display: inline-flex;
  align-items: center;
}

.breadcrumb-link:hover {
  color: #00d4ff;
  background: rgba(0, 212, 255, 0.15);
  transform: translateY(-1px);
}

.breadcrumb-current {
  color: #ffffff;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.breadcrumb-item.active .breadcrumb-current {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}
</style>