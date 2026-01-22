/**
 * Video Detection Page - Upload and detect rickshaws in videos
 * Now supports LIVE PREVIEW during processing
 */
import {useEffect, useRef, useState } from 'react';
import { detectVideoAsync, getJobStatus, getVideoStreamUrl, getStaticUrl } from '../api/client';
import UploadBox from '../components/UploadBox';
import VideoPlayer from '../components/VideoPlayer';
import Loader from '../components/Loader';

const VideoDetection = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [enableCounting, setEnableCounting] = useState(true);
  const [cameraId, setCameraId] = useState('default');
  
  // Live preview state
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [showLivePreview, setShowLivePreview] = useState(false);
  const statusCheckInterval = useRef(null);

  // Cleanup on unmount or when job completes
  useEffect(() => {
    return () => {
      if (statusCheckInterval.current) {
        clearInterval(statusCheckInterval.current);
      }
    };
  }, []);

  // Poll job status when processing
  useEffect(() => {
    if (jobId && loading) {
      // Check status every 2 seconds
      statusCheckInterval.current = setInterval(async () => {
        try {
          const status = await getJobStatus(jobId);
          setJobStatus(status);
          
          // If completed, fetch final results
          if (status.status === 'completed') {
            clearInterval(statusCheckInterval.current);
            setLoading(false);
            setShowLivePreview(false);
            setResult(status.result);
          }
          
          // If failed, show error
          if (status.status === 'failed') {
            clearInterval(statusCheckInterval.current);
            setLoading(false);
            setShowLivePreview(false);
            setError(status.error || 'Video processing failed');
          }
        } catch (err) {
          console.error('Error checking job status:', err);
        }
      }, 2000);
      
      return () => {
        if (statusCheckInterval.current) {
          clearInterval(statusCheckInterval.current);
        }
      };
    }
  }, [jobId, loading]);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setResult(null);
    setError(null);
    setJobId(null);
    setJobStatus(null);
    setShowLivePreview(false);
  };

  const handleDetection = async () => {
    if (!selectedFile) {
      setError('Please select a video file');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);
      setShowLivePreview(false);
      
      // Start async video processing with live preview
      const response = await detectVideoAsync(selectedFile, enableCounting, cameraId);
      
      // Store job ID and enable live preview
      setJobId(response.job_id);
      setShowLivePreview(true);
      
      console.log('Video processing started:', response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start video processing');
      setLoading(false);
      setShowLivePreview(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Upload Video</h2>
        <p className="text-gray-600 mb-6">
          Upload a video to detect rickshaws with entry/exit counting. Supported formats: MP4, AVI, MOV, MKV
        </p>

        <UploadBox
          onFileSelect={handleFileSelect}
          accept="video/*"
          maxSize={500 * 1024 * 1024}
          label="Upload Video"
        />

        {selectedFile && !result && (
          <div className="mt-6 space-y-4">
            {/* Configuration Options */}
            <div className="border-t pt-4 space-y-3">
              <h3 className="font-semibold text-gray-700">Detection Options</h3>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="enableCounting"
                  checked={enableCounting}
                  onChange={(e) => setEnableCounting(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <label htmlFor="enableCounting" className="ml-2 text-gray-700">
                  Enable Entry/Exit Counting
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Camera ID
                </label>
                <input
                  type="text"
                  value={cameraId}
                  onChange={(e) => setCameraId(e.target.value)}
                  placeholder="Enter camera identifier"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <button
              onClick={handleDetection}
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium text-lg"
            >
              {loading ? 'Processing...' : 'Process Video'}
            </button>
          </div>
        )}
      </div>

      {loading && (
        <div className="bg-white rounded-lg shadow-md p-8">
          {/* Live Preview Section */}
          {showLivePreview && jobId && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Live Processing Preview
              </h3>
              
              {/* MJPEG Stream - Live Preview */}
              <div className="relative bg-gray-900 rounded-lg overflow-hidden">
                <img
                  src={getVideoStreamUrl(jobId)}
                  alt="Live Processing Preview"
                  className="w-full h-auto"
                  onError={(e) => {
                    console.error('Stream error:', e);
                    e.target.style.display = 'none';
                  }}
                />
              </div>
              
              {/* Progress Bar */}
              {jobStatus && (
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Processing...</span>
                    <span>{Math.round(jobStatus.progress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                      style={{ width: `${jobStatus.progress}%` }}
                    ></div>
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    Frame {jobStatus.processed_frames} of {jobStatus.total_frames}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Fallback Loader if no live preview yet */}
          {!showLivePreview && (
            <>
              <Loader size="large" message="Starting video processing..." />
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-600">
                  Live preview will appear shortly...
                </p>
              </div>
            </>
          )}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <svg className="w-6 h-6 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-800">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Dismiss
          </button>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <svg className="w-6 h-6 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-green-800 font-medium">Video Processing Complete!</p>
              </div>
              <button
                onClick={() => {
                  setResult(null);
                  setSelectedFile(null);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Process Another Video
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Detection Results</h3>
            
            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600">Max Rickshaws</p>
                <p className="text-2xl font-bold text-purple-600">{result.rickshaw_count}</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600">Total Entry</p>
                <p className="text-2xl font-bold text-green-600">{result.total_entry}</p>
              </div>
              <div className="bg-red-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600">Total Exit</p>
                <p className="text-2xl font-bold text-red-600">{result.total_exit}</p>
              </div>
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600">Net Count</p>
                <p className="text-2xl font-bold text-blue-600">{result.net_count}</p>
              </div>
            </div>

            {/* Processed Video */}
            <VideoPlayer
              videoUrl={getStaticUrl(result.output_url)}
              entryCount={result.total_entry}
              exitCount={result.total_exit}
              netCount={result.net_count}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoDetection;
