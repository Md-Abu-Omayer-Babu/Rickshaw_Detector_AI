/**
 * LiveVideoPreview Component
 * 
 * Displays live MJPEG stream during video processing, shows progress,
 * and automatically transitions to final processed video when complete.
 * 
 * Props:
 * - jobId: string (required) - The job ID for the video processing task
 * - onComplete: function (optional) - Callback when processing completes with result data
 * - onError: function (optional) - Callback when processing fails with error message
 */
import { useState, useEffect, useRef } from 'react';
import { getJobStatus, getVideoStreamUrl, getStaticUrl } from '../api/client';
import Loader from './Loader';

const LiveVideoPreview = ({ jobId, onComplete, onError }) => {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(true);
  const [finalResult, setFinalResult] = useState(null);
  const statusCheckInterval = useRef(null);
  const streamImgRef = useRef(null);

  // Poll job status
  useEffect(() => {
    if (!jobId) return;

    const checkStatus = async () => {
      try {
        const statusData = await getJobStatus(jobId);
        setStatus(statusData);

        // Handle completion
        if (statusData.status === 'completed') {
          setIsProcessing(false);
          setFinalResult(statusData.result);
          
          // Clear interval
          if (statusCheckInterval.current) {
            clearInterval(statusCheckInterval.current);
            statusCheckInterval.current = null;
          }

          // Call onComplete callback
          if (onComplete) {
            onComplete(statusData.result);
          }
        }

        // Handle failure
        if (statusData.status === 'failed') {
          setIsProcessing(false);
          const errorMsg = statusData.error || 'Video processing failed';
          setError(errorMsg);
          
          // Clear interval
          if (statusCheckInterval.current) {
            clearInterval(statusCheckInterval.current);
            statusCheckInterval.current = null;
          }

          // Call onError callback
          if (onError) {
            onError(errorMsg);
          }
        }
      } catch (err) {
        console.error('Error checking job status:', err);
        const errorMsg = err.response?.data?.detail || 'Failed to check processing status';
        setError(errorMsg);
        
        if (statusCheckInterval.current) {
          clearInterval(statusCheckInterval.current);
          statusCheckInterval.current = null;
        }

        if (onError) {
          onError(errorMsg);
        }
      }
    };

    // Initial check
    checkStatus();

    // Poll every 2 seconds
    statusCheckInterval.current = setInterval(checkStatus, 2000);

    // Cleanup on unmount
    return () => {
      if (statusCheckInterval.current) {
        clearInterval(statusCheckInterval.current);
      }
    };
  }, [jobId, onComplete, onError]);

  // Handle stream image errors
  const handleStreamError = (e) => {
    console.error('MJPEG stream error:', e);
    // Don't hide the image, just log the error
    // Stream might recover or job might be completing
  };

  // Error state
  if (error && !isProcessing) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <svg 
            className="w-8 h-8 text-red-500 mr-3" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
            />
          </svg>
          <h3 className="text-lg font-semibold text-red-800">Processing Failed</h3>
        </div>
        <p className="text-red-700 mb-4">{error}</p>
        <div className="text-sm text-red-600">
          <p>Job ID: <code className="bg-red-100 px-2 py-1 rounded">{jobId}</code></p>
        </div>
      </div>
    );
  }

  // Final result - show processed video
  if (finalResult && !isProcessing) {
    return (
      <div className="space-y-4">
        {/* Success Banner */}
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg 
              className="w-6 h-6 text-green-500 mr-2" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" 
              />
            </svg>
            <span className="text-green-800 font-semibold">Processing Complete!</span>
          </div>
        </div>

        {/* Statistics Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-purple-50 rounded-lg p-4 text-center border border-purple-200">
            <p className="text-sm text-gray-600 mb-1">Max Detected</p>
            <p className="text-2xl font-bold text-purple-600">{finalResult.rickshaw_count}</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4 text-center border border-green-200">
            <p className="text-sm text-gray-600 mb-1">Total Entry</p>
            <p className="text-2xl font-bold text-green-600">{finalResult.total_entry}</p>
          </div>
          <div className="bg-red-50 rounded-lg p-4 text-center border border-red-200">
            <p className="text-sm text-gray-600 mb-1">Total Exit</p>
            <p className="text-2xl font-bold text-red-600">{finalResult.total_exit}</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 text-center border border-blue-200">
            <p className="text-sm text-gray-600 mb-1">Net Count</p>
            <p className="text-2xl font-bold text-blue-600">{finalResult.net_count}</p>
          </div>
        </div>

        {/* Final Processed Video */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Processed Video</h3>
          <div className="relative bg-black rounded-lg overflow-hidden">
            <video
              controls
              className="w-full h-auto"
              src={getStaticUrl(finalResult.output_url)}
              preload="metadata"
            >
              Your browser does not support the video tag.
            </video>
          </div>
          <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
            <span>File: {finalResult.file_name}</span>
            <a
              href={getStaticUrl(finalResult.output_url)}
              download
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Download Video
            </a>
          </div>
        </div>
      </div>
    );
  }

  // Processing state - show live MJPEG stream
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-gray-800">
            Live Processing Preview
          </h3>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-gray-600">LIVE</span>
          </div>
        </div>

        {/* MJPEG Stream Display */}
        <div className="relative bg-gray-900 rounded-lg overflow-hidden min-h-[400px] flex items-center justify-center">
          {isProcessing && jobId ? (
            <img
              ref={streamImgRef}
              src={getVideoStreamUrl(jobId)}
              alt="Live Processing Preview"
              className="w-full h-auto"
              onError={handleStreamError}
              style={{ display: 'block' }}
            />
          ) : (
            <Loader size="large" message="Initializing stream..." />
          )}
        </div>

        {/* Progress Information */}
        {status && (
          <div className="space-y-3">
            {/* Progress Bar */}
            <div>
              <div className="flex items-center justify-between text-sm text-gray-700 mb-2">
                <span className="font-medium">Processing Progress</span>
                <span className="font-bold text-blue-600">
                  {Math.round(status.progress || 0)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out relative"
                  style={{ width: `${status.progress || 0}%` }}
                >
                  <div className="absolute inset-0 bg-white opacity-20 animate-pulse"></div>
                </div>
              </div>
            </div>

            {/* Frame Counter */}
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center space-x-2">
                <svg 
                  className="w-5 h-5 text-gray-600" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" 
                  />
                </svg>
                <span className="text-sm font-medium text-gray-700">Frames Processed:</span>
              </div>
              <span className="text-sm font-bold text-gray-900">
                {status.processed_frames || 0} / {status.total_frames || 0}
              </span>
            </div>

            {/* Status Info */}
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <svg 
                  className="w-4 h-4 animate-spin text-blue-600" 
                  fill="none" 
                  viewBox="0 0 24 24"
                >
                  <circle 
                    className="opacity-25" 
                    cx="12" 
                    cy="12" 
                    r="10" 
                    stroke="currentColor" 
                    strokeWidth="4"
                  ></circle>
                  <path 
                    className="opacity-75" 
                    fill="currentColor" 
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span>Processing video with AI detection...</span>
              </div>
            </div>

            {/* Job ID (for debugging) */}
            <details className="text-xs">
              <summary className="cursor-pointer text-gray-500 hover:text-gray-700">
                Technical Details
              </summary>
              <div className="mt-2 p-2 bg-gray-100 rounded text-gray-700 font-mono">
                <p>Job ID: {jobId}</p>
                <p>Status: {status.status}</p>
              </div>
            </details>
          </div>
        )}

        {/* Loading state when no status yet */}
        {!status && isProcessing && (
          <div className="text-center py-4">
            <Loader size="medium" message="Fetching processing status..." />
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveVideoPreview;
