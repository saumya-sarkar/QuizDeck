<template>
  <div class="csv-export-container">
    <div class="glass-card">
      <div class="export-header mb-4">
        <h4 class="text-white">
          <font-awesome-icon icon="download" class="me-2" />
          Export User Quiz Attempts
        </h4>
        <p class="text-white-50">Download detailed reports of all user quiz attempts</p>
      </div>

      <!-- Period Selection -->
      <div class="row mb-4">
        <div class="col-md-6">
          <label class="form-label text-white">Time Period</label>
          <select v-model="selectedPeriod" class="form-select glass-input">
            <option value="last_30_days">Last 30 Days</option>
            <option value="all_time">All Time</option>
          </select>
        </div>
      </div>

      <!-- Action Button -->
      <div class="action-buttons mb-4">
        <button 
          class="btn btn-primary me-3"
          @click="generateAndDownload"
          :disabled="isProcessing"
        >
          <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2"></span>
          <font-awesome-icon v-else icon="download" class="me-2" />
          {{ isProcessing ? processingMessage : 'Generate & Download CSV' }}
        </button>
      </div>

      <!-- Status Message -->
      <div v-if="statusMessage" class="alert alert-info glass-alert">
        <font-awesome-icon icon="info-circle" class="me-2" />
        {{ statusMessage }}
      </div>

      <!-- Info Box -->
      <div class="info-box mt-4">
        <div class="info-content">
          <h6 class="text-white mb-2">
            <font-awesome-icon icon="info-circle" class="me-2" />
            Export Details
          </h6>
          <ul class="info-list text-white-50">
            <li>Contains all quiz attempts with user details</li>
            <li>Includes scores, timing, and completion status</li>
            <li>Organized by attempt date (newest first)</li>
            <li>CSV format compatible with Excel and Google Sheets</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import BASE_URL from '@/config/apiConfig';
import { useToast } from 'vue-toastification';

export default {
  name: 'SimpleCSVExport',
  data() {
    return {
      selectedPeriod: 'last_30_days',
      isProcessing: false,
      processingMessage: 'Generating...',
      statusMessage: '',
      currentTaskId: null
    };
  },

  methods: {
    async generateAndDownload() {
      const toast = useToast();
      this.isProcessing = true;
      this.statusMessage = '';
      this.processingMessage = 'Starting export...';

      try {
        // Step 1: Start the export
        const token = sessionStorage.getItem('access_token');
        
        const startResponse = await axios.post(`${BASE_URL}/csv-export/generate`, {
          period: this.selectedPeriod
        }, {
          headers: { 'Authorization': token }
        });

        if (startResponse.data.code === 200) {
          this.currentTaskId = startResponse.data.task_id;
          this.processingMessage = 'Generating CSV...';
          toast.info('Export started! Please wait...');
          
          // Step 2: Wait for completion and download
          await this.waitAndDownload();
        }
      } catch (error) {
        console.error('Error generating export:', error);
        toast.error(error.response?.data?.error_message || 'Failed to generate export');
      } finally {
        this.isProcessing = false;
        this.processingMessage = 'Generating...';
      }
    },

    async waitAndDownload() {
      const toast = useToast();
      const maxAttempts = 60; // Wait up to 5 minutes (60 * 5 seconds)
      let attempts = 0;

      const checkStatus = async () => {
        try {
          const token = sessionStorage.getItem('access_token');
          
          const statusResponse = await axios.post(`${BASE_URL}/csv-export/status`, {
            task_id: this.currentTaskId
          }, {
            headers: { 'Authorization': token }
          });

          if (statusResponse.data.code === 200) {
            const status = statusResponse.data.status;
            
            if (status === 'completed') {
              // Export completed, now download
              this.processingMessage = 'Downloading...';
              await this.downloadFile();
              return true; // Stop checking
            } else if (status === 'failed') {
              throw new Error(statusResponse.data.error_message || 'Export failed');
            } else {
              // Still processing
              attempts++;
              this.processingMessage = `Generating CSV... (${attempts * 5}s)`;
              
              if (attempts >= maxAttempts) {
                throw new Error('Export timeout - please try again');
              }

              // Check again in 3 seconds
              setTimeout(checkStatus, 3000);
              return false;
            }
          }
        } catch (error) {
          toast.error(error.message || 'Error checking export status');
          this.isProcessing = false;
          return true; // Stop checking
        }
      };

      // Start checking
      await checkStatus();
    },

    async downloadFile() {
      
      try {
      
        const toast = useToast();
        toast.success('CSV exported and downloaded successfully!');
        this.statusMessage = 'Export completed successfully!';
        window.location.href = `${BASE_URL}/csv-export/download/${this.currentTaskId}`;
        
      } catch (error) {
        console.error('Error downloading export:', error);
        const toast = useToast();
        toast.error('Failed to download export file');
      }
    }
  }
};
</script>

<style scoped>
.csv-export-container {
  padding: 2rem;
}

.glass-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.glass-input {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  backdrop-filter: blur(10px);
}

.glass-input:focus {
  background: rgba(255, 255, 255, 0.15) !important;
  border-color: rgba(255, 255, 255, 0.4) !important;
  box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25) !important;
  color: white !important;
}

.glass-input option {
  background: #1a1a1a;
  color: white;
}

.form-label {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.export-header h4 {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.action-buttons {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 25px;
  padding: 0.75rem 2rem;
  font-weight: 600;
  min-width: 250px;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.glass-alert {
  background: rgba(13, 202, 240, 0.2) !important;
  border: 1px solid rgba(13, 202, 240, 0.3) !important;
  border-radius: 15px !important;
  backdrop-filter: blur(10px);
  color: #ffffff !important;
}

.info-box {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
}

.info-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.info-list li {
  padding: 0.25rem 0;
  position: relative;
  padding-left: 1.5rem;
}

.info-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #28a745;
  font-weight: bold;
}
</style>