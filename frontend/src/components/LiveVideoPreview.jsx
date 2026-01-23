import { useState, useEffect, useRef } from 'react';
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

/**
 * LiveVideoPreview Component
 * 
 * Displays live MJPEG stream during video processing, then switches to final video when complete.
 * 
 * @param {string} jobId - The unique job ID for the video processing task
 * @param {function} onComplete - Optional callback when processing completes successfully
 * @param {function} onError - Optional callback when processing fails
 */
const LiveVideoPreview = ({ jobId, onComplete, onError }) => {
  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(true);
  const [finalVideoUrl, setFinalVideoUrl] = useState(null);
  const pollIntervalRef = useRef(null);
  const videoRef = useRef(null);

  // Poll for job status every 2 seconds
  useEffect(() => {
    if (!jobId) return;

    const fetchJobStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/detect/video/status/${jobId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch job status: ${response.statusText}`);
        }

        const data = await response.json();
        setJobStatus(data);

        // Check if processing is complete
        if (data.status === 'completed') {
          setIsProcessing(false);
          setFinalVideoUrl(`${API_BASE_URL}/outputs/videos/${jobId}.mp4`);
          
          // Stop polling
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
          }

          // Trigger completion callback
          if (onComplete) {
            onComplete(data);
          }
        } else if (data.status === 'failed' || data.status === 'error') {
          setIsProcessing(false);
          setError(data.error || 'Video processing failed');
          
          // Stop polling
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
          }

          // Trigger error callback
          if (onError) {
            onError(data.error || 'Video processing failed');
          }
        }
      } catch (err) {
        console.error('Error fetching job status:', err);
        setError(err.message);
        setIsProcessing(false);
        
        // Stop polling on error
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
        }

        if (onError) {
          onError(err.message);
        }
      }
    };

    // Initial fetch
    fetchJobStatus();

    // Start polling every 2 seconds
    pollIntervalRef.current = setInterval(fetchJobStatus, 2000);

    // Cleanup on unmount
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [jobId, onComplete, onError]);

  // Auto-play final video when loaded
  useEffect(() => {
    if (finalVideoUrl && videoRef.current) {
      videoRef.current.load();
      videoRef.current.play().catch(err => {
        console.log('Auto-play prevented:', err);
      });
    }
  }, [finalVideoUrl]);

  if (!jobId) {
    return (
      <div className="flex items-center justify-center p-8 bg-gray-50 rounded-lg">
        <p className="text-gray-500">No job ID provided</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start space-x-4">
          <AlertCircle className="w-6 h-6 text-red-600 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-red-900 mb-2">Processing Failed</h3>
            <p className="text-red-700">{error}</p>
            <p className="text-sm text-red-600 mt-2">Job ID: {jobId}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Status Header */}
      <div className="mb-4 bg-white rounded-lg shadow-sm p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            {isProcessing ? (
              <>
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                <span className="font-semibold text-gray-900">Processing Video...</span>
              </>
            ) : (
              <>
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <span className="font-semibold text-gray-900">Processing Complete</span>
              </>
            )}
          </div>
          {jobStatus && (
            <span className="text-sm font-medium text-gray-600">
              {jobStatus.progress}% Complete
            </span>
          )}
        </div>

        {/* Progress Bar */}
        {jobStatus && (
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-blue-600 h-full rounded-full transition-all duration-500 ease-out"
              style={{ width: `${jobStatus.progress}%` }}
            />
          </div>
        )}

        {/* Stats */}
        {jobStatus && (
          <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
            <div className="flex flex-col">
              <span className="text-gray-500">Status</span>
              <span className="font-medium text-gray-900 capitalize">{jobStatus.status}</span>
            </div>
            {jobStatus.total_frames > 0 && (
              <div className="flex flex-col">
                <span className="text-gray-500">Frames</span>
                <span className="font-medium text-gray-900">
                  {jobStatus.processed_frames} / {jobStatus.total_frames}
                </span>
              </div>
            )}
            {jobStatus.entry_count !== undefined && (
              <div className="flex flex-col">
                <span className="text-gray-500">Entries</span>
                <span className="font-medium text-green-600">{jobStatus.entry_count}</span>
              </div>
            )}
            {jobStatus.exit_count !== undefined && (
              <div className="flex flex-col">
                <span className="text-gray-500">Exits</span>
                <span className="font-medium text-red-600">{jobStatus.exit_count}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Video Display */}
      <div className="bg-gray-900 rounded-lg overflow-hidden shadow-lg">
        {isProcessing ? (
          // MJPEG Live Stream
          <div className="relative">
            <img
              src={`${API_BASE_URL}/api/stream/video/${jobId}`}
              alt="Live Processing Stream"
              className="w-full h-auto object-contain"
              onError={(e) => {
                console.error('MJPEG stream error');
                // Keep trying to load the stream
                setTimeout(() => {
                  e.target.src = `${API_BASE_URL}/api/stream/video/${jobId}?t=${Date.now()}`;
                }, 2000);
              }}
            />
            <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm font-semibold flex items-center space-x-2 shadow-lg">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
              <span>LIVE</span>
            </div>
          </div>
        ) : finalVideoUrl ? (
          // Final Processed Video
          <div className="relative">
            <video
              ref={videoRef}
              className="w-full h-auto"
              controls
              loop
              playsInline
            >
              <source src={finalVideoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
            <div className="absolute top-4 left-4 bg-green-600 text-white px-3 py-1 rounded-full text-sm font-semibold shadow-lg">
              ✓ Processed
            </div>
          </div>
        ) : (
          // Loading State
          <div className="flex items-center justify-center h-96 bg-gray-800">
            <div className="text-center">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
              <p className="text-gray-300">Loading video...</p>
            </div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="mt-4 text-center text-sm text-gray-500">
        Job ID: <span className="font-mono">{jobId}</span>
      </div>
    </div>
  );
};

export default LiveVideoPreview;
