import { createApp } from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";


// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';

// Import Bootstrap JavaScript (optional, if you need interactive components)
// Bootstrap 5 uses Popper.js internally, so bootstrap.bundle.min.js includes Popper.
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// Font Awesome Setup
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';


import { 
  faEye, faEyeSlash, faPlay, faInfoCircle, faUsers, faBook, faList, faClipboardCheck,
  faQuestionCircle, faBookOpen, faEdit, faTrash, faCircleExclamation, faUser, faLock, faRotateLeft, 
  faCircleCheck, faTableColumns, faChartLine, faAdd, faArrowLeft, faCheck, faPlayCircle, faGraduationCap,faPenNib, 
  faClock, faTrophy, faCalendar, faStopCircle, faClipboardQuestion, faTimes, faDownload, faSearch,
  faHourglassStart, faHourglassEnd, faCheckCircle, faInfinity,
  faChevronLeft, faChevronRight, faSave, faPaperPlane, faExclamationTriangle, faAward, faTimesCircle,
  faTachometerAlt, faSpinner, faRedo, faShare,
  faMedal, faClipboardList,
  faChartPie,
  faHistory,
  faUserCheck,
  faEnvelope
} from '@fortawesome/free-solid-svg-icons';

// Import brand icons for social media
import {faFacebookF, faTwitter, faInstagram, faLinkedinIn} from '@fortawesome/free-brands-svg-icons'; // Footer icons

// Add any icons you want to use
library.add(
  faEye, 
  faEyeSlash, 
  faPlay,
  faInfoCircle,
  faUsers,
  faBook,
  faQuestionCircle,
  faBookOpen,
  faEdit,
  faTrash,
  faCircleExclamation,
  faUser,
  faLock,
  faRotateLeft,
  faCircleCheck,
  faTableColumns,
  faList,
  faClipboardCheck,
  faChartLine,
  faAdd,
  faArrowLeft,
  faCheck,
  faPlayCircle,
  faGraduationCap,
  faPenNib,
  faClock,
  faTrophy,
  faCalendar,
  faStopCircle,
  faClipboardQuestion,
  faTimes,
  faDownload,
  faSearch,
  faHourglassStart,
  faHourglassEnd,
  faCheckCircle,
  faInfinity,
  faChevronLeft,
  faChevronRight,
  faSave,
  faPaperPlane,
  faExclamationTriangle,
  faAward,
  faTimesCircle,
  faTachometerAlt,
  faSpinner,
  faRedo,
  faShare,
  faMedal,
  faClipboardList,
  faChartPie,
  faHistory,
  faUserCheck,
  faEnvelope,
  // Brand icons
  faFacebookF,
  faTwitter,
  faInstagram,
  faLinkedinIn
);


const app = createApp(App);

// Register Font Awesome icon component globally
// This allows you to use <font-awesome-icon> in your templates
app.component('font-awesome-icon', FontAwesomeIcon);

app.use(store);
app.use(router);
app.use(Toast, {
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  icon: true
});
app.mount('#app');
