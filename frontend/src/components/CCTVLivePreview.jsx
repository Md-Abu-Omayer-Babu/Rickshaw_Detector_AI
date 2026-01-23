/**
 * CCTVLivePreview Component
 * 
 * Displays real-time CCTV/RTSP stream with live YOLO detection.
 * Shows MJPEG stream from backend with bounding boxes, entry-exit line, and live counts.
 * 
 * @param {string} cameraId - Required: Unique camera identifier
 * @param {function} onError - Optional: Callback when stream encounters an error
 * @param {function} onStatusUpdate - Optional: Callback with live status updates
 */
import { useState, useEffect, useRef } from 'react';
import { AlertCircle, Wifi, WifiOff, Loader2 } from 'lucide-react';
import { getCCTVStatus, getCCTVStreamUrl } from '../api/client';

const CCTVLivePreview = ({ cameraId, onError, onStatusUpdate }) => {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [streamError, setStreamError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const pollIntervalRef = useRef(null);
  const imgRef = useRef(null);

  // Poll for camera status every 2 seconds
  useEffect(() => {
    // if (!cameraId) {
    //   setError('Camera ID is required');
    //   return;
    // }

    const fetchStatus = async () => {
      try {
        const data = await getCCTVStatus(cameraId);
        setStatus(data);
        
        // Update loading state based on status
        if (data.status === 'streaming') {
          setIsLoading(false);
        }

        // Notify parent component of status updates
        if (onStatusUpdate) {
          onStatusUpdate(data);
        }

        // Handle error status
        if (data.status === 'error') {
          const errorMsg = data.error_message || 'Camera stream error';
          setError(errorMsg);
          setIsLoading(false);
          
          if (onError) {
            onError(errorMsg);
          }
        }

        // Handle stopped status
        if (data.status === 'stopped') {
          setIsLoading(false);
        }
      } catch (err) {
        const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch camera status';
        console.error('Status fetch error:', err);
        setError(errorMsg);
        setIsLoading(false);
        
        if (onError) {
          onError(errorMsg);
        }
      }
    };

    // Initial fetch
    fetchStatus();

    // Start polling every 2 seconds
    pollIntervalRef.current = setInterval(fetchStatus, 2000);

    // Cleanup on unmount
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [cameraId, onError, onStatusUpdate]);

  // Handle image load success
  const handleImageLoad = () => {
    setIsLoading(false);
    setStreamError(false);
  };

  // Handle image load error
  const handleImageError = () => {
    setStreamError(true);
    setIsLoading(false);
  };

  // Get stream URL with cache-busting
  const streamUrl = cameraId ? getCCTVStreamUrl(cameraId) : null;

  // Render error state
  if (error && !status) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start space-x-4">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-red-900 mb-2">Camera Error</h3>
            <p className="text-red-700">{error}</p>
            <p className="text-sm text-red-600 mt-2">Camera ID: {cameraId}</p>
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
            {status?.status === 'streaming' ? (
              <>
                <Wifi className="w-5 h-5 text-green-600" />
                <span className="font-semibold text-gray-900">Live Streaming</span>
              </>
            ) : status?.status === 'connecting' ? (
              <>
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                <span className="font-semibold text-gray-900">Connecting...</span>
              </>
            ) : status?.status === 'stopped' ? (
              <>
                <WifiOff className="w-5 h-5 text-gray-600" />
                <span className="font-semibold text-gray-900">Stopped</span>
              </>
            ) : (
              <>
                <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
                <span className="font-semibold text-gray-900">Initializing...</span>
              </>
            )}
          </div>
          {status && (
            <span className="text-sm font-medium text-gray-600">
              {status.camera_name || cameraId}
            </span>
          )}
        </div>

        {/* Live Statistics */}
        {status && status.status === 'streaming' && (
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-sm">
            <div className="flex flex-col">
              <span className="text-gray-500">Entry</span>
              <span className="font-bold text-green-600 text-lg">{status.entry_count}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-500">Exit</span>
              <span className="font-bold text-red-600 text-lg">{status.exit_count}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-500">Net Count</span>
              <span className="font-bold text-blue-600 text-lg">{status.net_count}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-500">FPS</span>
              <span className="font-medium text-gray-900">{status.fps.toFixed(1)}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-gray-500">Uptime</span>
              <span className="font-medium text-gray-900">{Math.floor(status.uptime)}s</span>
            </div>
          </div>
        )}

        {/* Stream Properties */}
        {status?.stream_properties && (
          <div className="mt-2 text-xs text-gray-500">
            Resolution: {status.stream_properties.width}×{status.stream_properties.height} @ {status.stream_properties.fps} FPS
          </div>
        )}

        {/* Error Message */}
        {status?.error_message && (
          <div className="mt-2 text-sm text-red-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1" />
            {status.error_message}
          </div>
        )}
      </div>

      {/* MJPEG Video Stream */}
      <div className="bg-gray-900 rounded-lg overflow-hidden shadow-lg relative">
        {/* Loading Overlay */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800 z-10">
            <div className="text-center">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
              <p className="text-gray-300">
                {status?.status === 'connecting' 
                  ? 'Connecting to camera...' 
                  : 'Loading stream...'}
              </p>
            </div>
          </div>
        )}

        {/* Stream Error Overlay */}
        {streamError && !isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800 z-10">
            <div className="text-center p-4">
              <WifiOff className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <p className="text-gray-300 mb-2">Stream unavailable</p>
              <p className="text-sm text-gray-400">
                Retrying connection...
              </p>
            </div>
          </div>
        )}

        {/* MJPEG Stream Image */}
        {streamUrl && (
          <img
            ref={imgRef}
            src={streamUrl}
            alt={`Live CCTV Feed - ${cameraId}`}
            className="w-full h-auto object-contain"
            onLoad={handleImageLoad}
            onError={handleImageError}
            style={{ 
              display: streamError ? 'none' : 'block',
              minHeight: '400px',
              maxHeight: '720px'
            }}
          />
        )}

        {/* Live Indicator */}
        {status?.status === 'streaming' && !isLoading && !streamError && (
          <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm font-semibold flex items-center space-x-2 shadow-lg">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            <span>LIVE</span>
          </div>
        )}

        {/* Frames Processed Counter */}
        {status?.frames_processed > 0 && !isLoading && !streamError && (
          <div className="absolute bottom-4 left-4 bg-black bg-opacity-60 text-white px-3 py-1 rounded text-xs">
            Frames: {status.frames_processed}
          </div>
        )}
      </div>

      {/* Camera Info Footer */}
      <div className="mt-4 text-center text-sm text-gray-500">
        Camera ID: <span className="font-mono">{cameraId}</span>
        {status?.status === 'stopped' && (
          <span className="ml-2 text-red-600">● Stream Stopped</span>
        )}
      </div>
    </div>
  );
};

export default CCTVLivePreview;
