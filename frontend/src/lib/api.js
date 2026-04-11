import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const api = {
  // Classes
  getClasses: () => axios.get(`${API}/classes`),
  createClass: (data) => axios.post(`${API}/classes`, data),
  updateClass: (id, data) => axios.put(`${API}/classes/${id}`, data),
  deleteClass: (id) => axios.delete(`${API}/classes/${id}`),

  // Fee Types
  getFeeTypes: (params) => axios.get(`${API}/fee-types`, { params }),
  createFeeType: (data) => axios.post(`${API}/fee-types`, data),
  updateFeeType: (id, data) => axios.put(`${API}/fee-types/${id}`, data),
  deleteFeeType: (id) => axios.delete(`${API}/fee-types/${id}`),

  // Students
  getStudents: (params) => axios.get(`${API}/students`, { params }),
  createStudent: (data) => axios.post(`${API}/students`, data),
  bulkUploadStudents: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post(`${API}/students/bulk`, formData);
  },
  getSampleCSV: () => axios.get(`${API}/students/sample-csv`, { responseType: 'blob' }),
  updateStudent: (id, data) => axios.put(`${API}/students/${id}`, data),
  deleteStudent: (id) => axios.delete(`${API}/students/${id}`),
  promoteStudents: (data) => axios.post(`${API}/students/promote`, data),

  // Attendance
  markAttendance: (data) => axios.post(`${API}/attendance`, data),
  getAttendance: (params) => axios.get(`${API}/attendance`, { params }),
  exportAttendance: (params) => axios.get(`${API}/attendance/export`, { params, responseType: 'blob' }),
  sendAttendanceAlerts: (data) => axios.post(`${API}/attendance/send-alerts`, data),

  // Fees
  getStudentFees: (rollNo) => axios.get(`${API}/fees/student/${rollNo}`),
  createFeePayment: (data) => axios.post(`${API}/fees/payment`, data),
  getDaySheet: (date) => axios.get(`${API}/fees/day-sheet`, { params: { date } }),
  exportFees: (params) => axios.get(`${API}/fees/export`, { params, responseType: 'blob' }),

  // Expenses
  getExpenses: (params) => axios.get(`${API}/expenses`, { params }),
  createExpense: (data) => axios.post(`${API}/expenses`, data),

  // Settings
  getWhatsAppSettings: () => axios.get(`${API}/settings/whatsapp`),
  updateWhatsAppSettings: (data) => axios.put(`${API}/settings/whatsapp`, data),
  getDatabaseSettings: () => axios.get(`${API}/settings/database`),
  updateDatabaseSettings: (data) => axios.put(`${API}/settings/database`, data),

  // Upload
  uploadFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post(`${API}/upload`, formData);
  },

  // Dashboard
  getDashboardStats: () => axios.get(`${API}/stats/dashboard`),

  // Student Detail
  getStudentDetail: (id) => axios.get(`${API}/students/${id}/detail`),

  // Inventory
  getInventory: (params) => axios.get(`${API}/inventory`, { params }),
  createInventory: (data) => axios.post(`${API}/inventory`, data),
  updateInventory: (id, data) => axios.put(`${API}/inventory/${id}`, data),
  deleteInventory: (id) => axios.delete(`${API}/inventory/${id}`),

  // Events
  getEvents: (params) => axios.get(`${API}/events`, { params }),
  createEvent: (data) => axios.post(`${API}/events`, data),
  deleteEvent: (id) => axios.delete(`${API}/events/${id}`),

  // Homework
  getHomework: (params) => axios.get(`${API}/homework`, { params }),
  createHomework: (data) => axios.post(`${API}/homework`, data),
  deleteHomework: (id) => axios.delete(`${API}/homework/${id}`),

  // Fee Reminders
  sendFeeReminders: () => axios.post(`${API}/fees/send-reminders`),
};
