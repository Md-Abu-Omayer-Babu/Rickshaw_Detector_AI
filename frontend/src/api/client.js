/**
 * Axios API client configuration
 * Centralized HTTP client with interceptors and error handling
 */
import axios from 'axios';

// Base URL for the FastAPI backend
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 300000, // 5 minutes for video processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // You can add auth tokens here if needed
    // config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors globally
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (status === 400) {
        console.error('Bad Request:', data.detail || data.error);
      } else if (status === 404) {
        console.error('Not Found:', data.detail || data.error);
      } else if (status === 500) {
        console.error('Server Error:', data.detail || data.error);
      }
    } else if (error.request) {
      // Request was made but no response
      console.error('Network Error: No response from server');
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API endpoint functions

/**
 * Detection APIs
 */
export const detectImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/api/detect/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const detectVideo = async (file, enableCounting = true, cameraId = 'default') => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post(
    `/api/detect/video?enable_counting=${enableCounting}&camera_id=${cameraId}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  
  return response.data;
};

/**
 * Async video detection with live preview support
 * Returns job_id immediately for streaming
 */
export const detectVideoAsync = async (file, enableCounting = true, cameraId = 'default') => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post(
    `/api/detect/video/async?enable_counting=${enableCounting}&camera_id=${cameraId}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  
  return response.data;
};

/**
 * Get video processing job status
 */
export const getJobStatus = async (jobId) => {
  const response = await apiClient.get(`/api/detect/video/status/${jobId}`);
  return response.data;
};

/**
 * Pause video processing job
 */
export const pauseVideoJob = async (jobId) => {
  const response = await apiClient.post(`/api/detect/video/pause/${jobId}`);
  return response.data;
};

/**
 * Resume video processing job
 */
export const resumeVideoJob = async (jobId) => {
  const response = await apiClient.post(`/api/detect/video/resume/${jobId}`);
  return response.data;
};

/**
 * Stop video processing job
 */
export const stopVideoJob = async (jobId) => {
  const response = await apiClient.post(`/api/detect/video/stop/${jobId}`);
  return response.data;
};

/**
 * Skip forward in video processing
 */
export const forwardVideoJob = async (jobId, frames = 30) => {
  const response = await apiClient.post(`/api/detect/video/forward/${jobId}?frames=${frames}`);
  return response.data;
};

/**
 * Skip backward in video processing
 */
export const backwardVideoJob = async (jobId, frames = 30) => {
  const response = await apiClient.post(`/api/detect/video/backward/${jobId}?frames=${frames}`);
  return response.data;
};

/**
 * Get MJPEG stream URL for live video preview
 */
export const getVideoStreamUrl = (jobId) => {
  return `${BASE_URL}/api/stream/video/${jobId}`;
};

export const processCCTVStream = async (cameraId, rtspUrl, duration = 60, cameraName = '') => {
  const response = await apiClient.post('/api/cctv/stream', {
    camera_id: cameraId,
    rtsp_url: rtspUrl,
    duration: duration,
    camera_name: cameraName || cameraId,
  });
  
  return response.data;
};

export const testStreamConnection = async (cameraId, rtspUrl) => {
  const response = await apiClient.post('/api/cctv/stream/test', {
    camera_id: cameraId,
    rtsp_url: rtspUrl,
  });
  
  return response.data;
};

/**
 * NEW: Continuous CCTV streaming APIs
 */
export const startCCTVStream = async (cameraId, rtspUrl, cameraName = '') => {
  const response = await apiClient.post('/api/cctv/start', {
    camera_id: cameraId,
    rtsp_url: rtspUrl,
    camera_name: cameraName || cameraId,
  });
  
  return response.data;
};

export const stopCCTVStream = async (cameraId) => {
  const response = await apiClient.post(`/api/cctv/stop/${cameraId}`);
  return response.data;
};

export const getCCTVStatus = async (cameraId) => {
  const response = await apiClient.get(`/api/cctv/status/${cameraId}`);
  return response.data;
};

export const getCCTVStreamUrl = (cameraId) => {
  return `${BASE_URL}/api/stream/cctv/${cameraId}`;
};

export const listCCTVStreams = async () => {
  const response = await apiClient.get('/api/cctv/list');
  return response.data;
};

/**
 * Data APIs
 */
export const getHistory = async (filters = {}) => {
  const queryParams = new URLSearchParams();
  
  if (filters.start_date) queryParams.append('start_date', filters.start_date);
  if (filters.end_date) queryParams.append('end_date', filters.end_date);
  if (filters.file_type) queryParams.append('file_type', filters.file_type);
  
  const url = queryParams.toString() 
    ? `/api/history?${queryParams.toString()}`
    : '/api/history';
    
  const response = await apiClient.get(url);
  return response.data;
};

export const exportLogs = async (params = {}) => {
  const queryParams = new URLSearchParams();
  
  if (params.format) queryParams.append('format', params.format);
  if (params.start_date) queryParams.append('start_date', params.start_date);
  if (params.end_date) queryParams.append('end_date', params.end_date);
  if (params.event_type) queryParams.append('event_type', params.event_type);
  if (params.camera_id) queryParams.append('camera_id', params.camera_id);
  if (params.limit) queryParams.append('limit', params.limit);
  
  const response = await apiClient.get(`/api/export/logs?${queryParams.toString()}`, {
    responseType: params.format === 'csv' ? 'blob' : 'json',
  });
  
  return response;
};

/**
 * Analytics APIs
 */
export const getDashboardAnalytics = async (cameraId = 'default') => {
  const response = await apiClient.get(`/api/analytics/dashboard?camera_id=${cameraId}`);
  return response.data;
};

export const getDailyStats = async (date, cameraId = 'default') => {
  const response = await apiClient.get(`/api/analytics/daily?date=${date}&camera_id=${cameraId}`);
  return response.data;
};

/**
 * Utility function to get full URL for static files
 */
export const getStaticUrl = (path) => {
  if (!path) return '';
  // If path starts with /outputs, it's already correct
  if (path.startsWith('/outputs')) {
    return `${BASE_URL}${path}`;
  }
  // Otherwise, construct the full URL
  return `${BASE_URL}${path}`;
};

export default apiClient;
