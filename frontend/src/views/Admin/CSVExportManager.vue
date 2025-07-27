<template>
  <div class="csv-export-page">
    <Navbar />
    <div class="container-fluid py-4">
      <Breadcrumb :items="breadcrumbItems" />
      
      <div class="row mb-4">
        <div class="col-12">
          <h2 class="page-title mb-0">CSV Export</h2>
          <p class="text-muted mb-0">Export user quiz attempts data</p>
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <SimpleCSVExport />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import SimpleCSVExport from '@/components/Admin/SimpleCSVExport.vue';

export default {
  name: 'CSVExportManager',
  components: { Navbar, Breadcrumb, SimpleCSVExport },
  data() {
    return {
      breadcrumbItems: [{ name: 'CSV Export', icon: 'download' }]
    };
  }
};
</script>

<style scoped>
.csv-export-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
  position: relative;
}

.csv-export-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.container-fluid {
  max-width: 1400px;
  position: relative;
  z-index: 1;
}

.page-title {
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-muted {
  color: rgba(255, 255, 255, 0.7) !important;
}
</style>