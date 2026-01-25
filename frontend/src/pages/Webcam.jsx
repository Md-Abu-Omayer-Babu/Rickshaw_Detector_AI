/**
 * Webcam Streaming Page - Real-time Local Camera Detection
 * Optimized with frame skipping and MJPEG streaming
 */
import { useState, useEffect, useRef } from 'react';
import { startWebcamStream, stopWebcamStream, getWebcamStatus, getWebcamStreamUrl, listAvailableCameras } from '../api/client';
import Loader from '../components/Loader';
import { Camera, Video, VideoOff, Play, Square, Wifi, WifiOff, AlertCircle, CheckCircle, Settings } from 'lucide-react';

const Webcam = () => {
  // Form state
  const [cameraIndex, setCameraIndex] = useState(0);
  const [cameraName, setCameraName] = useState('Webcam');
  const [frameSkip, setFrameSkip] = useState(3);
  const [availableCameras, setAvailableCameras] = useState([]);
  
  // Stream state
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamStatus, setStreamStatus] = useState(null);
  const [streamError, setStreamError] = useState(false);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Refs
  const pollIntervalRef = useRef(null);
  const imgRef = useRef(null);

  // Load available cameras on mount
  useEffect(() => {
    loadAvailableCameras();
  }, []);

  // Poll stream status every 1.5 seconds
  useEffect(() => {
    if (!isStreaming) {
      return;
    }

    const fetchStatus = async () => {
      try {
        const data = await getWebcamStatus(cameraIndex);
        setStreamStatus(data);

        // Handle error status
        if (data.status === 'error') {
          setError(data.error_message || 'Stream encountered an error');
          setIsStreaming(false);
        }

        // Handle stopped status
        if (data.status === 'stopped') {
          setIsStreaming(false);
        }
      } catch (err) {
        console.error('Status fetch error:', err);
      }
    };

    // Initial fetch
    fetchStatus();

    // Poll every 1.5 seconds
    pollIntervalRef.current = setInterval(fetchStatus, 1500);

    // Cleanup
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [isStreaming, cameraIndex]);

  const loadAvailableCameras = async () => {
    try {
      const response = await listAvailableCameras();
      setAvailableCameras(response.cameras || []);
    } catch (err) {
      console.error('Failed to load cameras:', err);
    }
  };

  const handleStartStream = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);
      setStreamError(false);
      
      await startWebcamStream(cameraIndex, cameraName, frameSkip);
      setIsStreaming(true);
      setSuccessMessage('Webcam stream started successfully! Loading video...');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start webcam stream');
      setIsStreaming(false);
    } finally {
      setLoading(false);
    }
  };

  const handleStopStream = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);
      
      await stopWebcamStream(cameraIndex);
      setIsStreaming(false);
      setStreamStatus(null);
      setSuccessMessage('Webcam stream stopped successfully');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to stop webcam stream');
    } finally {
      setLoading(false);
    }
  };

  const handleImageLoad = () => {
    setStreamError(false);
  };

  const handleImageError = () => {
    setStreamError(true);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Information Banner */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <Camera className="w-6 h-6 text-blue-500 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-blue-800 font-medium">Real-time Webcam Detection</p>
            <p className="text-blue-700 text-sm mt-1">
              Stream from your local USB or IP webcam with optimized YOLOv8 detection. 
              Frame skipping ensures smooth performance without buffering.
            </p>
          </div>
        </div>
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
            <p className="text-green-800">{successMessage}</p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="w-6 h-6 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-red-800 font-medium">Error</p>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-500 hover:text-red-700 ml-4"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Configuration Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            <Video className="w-6 h-6 text-gray-700 mr-2" />
            <h2 className="text-2xl font-bold text-gray-800">Webcam Configuration</h2>
          </div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-sm text-blue-600 hover:text-blue-800"
          >
            <Settings className="w-4 h-4 mr-1" />
            {showAdvanced ? 'Hide' : 'Show'} Advanced
          </button>
        </div>
        <p className="text-gray-600 mb-6">
          Configure your local webcam for real-time detection
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Camera Device <span className="text-red-500">*</span>
            </label>
            <select
              value={cameraIndex}
              onChange={(e) => setCameraIndex(parseInt(e.target.value))}
              disabled={isStreaming}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              {availableCameras.length > 0 ? (
                availableCameras.map((cam) => (
                  <option key={cam.index} value={cam.index}>
                    Camera {cam.index} {cam.index === 0 ? '(Default)' : ''}
                  </option>
                ))
              ) : (
                <>
                  <option value={0}>Camera 0 (Default)</option>
                  <option value={1}>Camera 1</option>
                  <option value={2}>Camera 2</option>
                </>
              )}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Select camera device (0 for built-in webcam)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Camera Name (Optional)
            </label>
            <input
              type="text"
              value={cameraName}
              onChange={(e) => setCameraName(e.target.value)}
              placeholder="e.g., Front Webcam"
              disabled={isStreaming}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>

          {/* Advanced Settings */}
          {showAdvanced && (
            <div className="bg-gray-50 rounded-lg p-4 space-y-4">
              <h3 className="font-semibold text-gray-700 flex items-center">
                <Settings className="w-4 h-4 mr-2" />
                Performance Settings
              </h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Frame Skip (Process every Nth frame)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={frameSkip}
                  onChange={(e) => setFrameSkip(parseInt(e.target.value))}
                  disabled={isStreaming}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-600 mt-1">
                  <span>1 (Slowest, Most Accurate)</span>
                  <span className="font-semibold">Current: {frameSkip}</span>
                  <span>10 (Fastest, Less Accurate)</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Higher values = faster but less frequent detection. Recommended: 3
                </p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm">
                <p className="text-blue-800">
                  <strong>💡 Tip:</strong> If the video is laggy, increase frame skip to 4-5. 
                  For maximum accuracy, use frame skip of 1-2 (requires more CPU).
                </p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4">
            {!isStreaming ? (
              <button
                onClick={handleStartStream}
                disabled={loading}
                className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <Loader size="small" className="mr-2" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 mr-2" />
                    Start Webcam
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={handleStopStream}
                disabled={loading}
                className="flex-1 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <Loader size="small" className="mr-2" />
                    Stopping...
                  </>
                ) : (
                  <>
                    <Square className="w-5 h-5 mr-2" />
                    Stop Webcam
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Live Stream Viewer */}
      {isStreaming && (
        <div className="space-y-4">
          {/* Stream Status Header */}
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                {streamStatus?.status === 'streaming' ? (
                  <>
                    <div className="flex items-center">
                      <span className="w-3 h-3 bg-red-600 rounded-full animate-pulse mr-2"></span>
                      <Wifi className="w-5 h-5 text-green-600 mr-2" />
                    </div>
                    <div>
                      <span className="font-semibold text-gray-900">Live Streaming</span>
                      <p className="text-xs text-gray-500">
                        {streamStatus.camera_name || `Camera ${cameraIndex}`}
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <Loader size="small" className="mr-2" />
                    <span className="font-semibold text-gray-900">Initializing...</span>
                  </>
                )}
              </div>
              
              {streamStatus && (
                <div className="text-right text-sm">
                  <p className="text-gray-600">
                    Frame Skip: <span className="font-medium">{streamStatus.config?.frame_skip}</span>
                  </p>
                </div>
              )}
            </div>

            {/* Live Statistics */}
            {streamStatus && streamStatus.status === 'streaming' && (
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
                <div className="bg-green-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">Entry</p>
                  <p className="text-2xl font-bold text-green-600">{streamStatus.entry_count}</p>
                </div>
                <div className="bg-red-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">Exit</p>
                  <p className="text-2xl font-bold text-red-600">{streamStatus.exit_count}</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">Net Count</p>
                  <p className="text-2xl font-bold text-blue-600">{streamStatus.net_count}</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">FPS</p>
                  <p className="text-xl font-bold text-purple-600">{streamStatus.fps?.toFixed(1) || '0.0'}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-600 mb-1">Processed</p>
                  <p className="text-xl font-bold text-gray-700">{streamStatus.frames_processed || 0}</p>
                </div>
              </div>
            )}

            {/* Performance Info */}
            {streamStatus?.stream_properties && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="flex justify-between text-xs text-gray-600">
                  <span>
                    Resolution: {streamStatus.stream_properties.width}×{streamStatus.stream_properties.height}
                  </span>
                  <span>
                    Displayed: {streamStatus.frames_displayed} | Processed: {streamStatus.frames_processed}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Video Player */}
          <div className="bg-gray-900 rounded-lg overflow-hidden shadow-lg relative">
            {/* Stream Error Overlay */}
            {streamError && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-800 z-10">
                <div className="text-center p-4">
                  <WifiOff className="w-16 h-16 text-red-500 mx-auto mb-4" />
                  <p className="text-gray-300 text-lg mb-2">Stream Unavailable</p>
                  <p className="text-sm text-gray-400">
                    Waiting for webcam connection...
                  </p>
                </div>
              </div>
            )}

            {/* MJPEG Stream */}
            <img
              ref={imgRef}
              src={getWebcamStreamUrl(cameraIndex)}
              alt={`Webcam Stream - Camera ${cameraIndex}`}
              className="w-full h-auto object-contain"
              onLoad={handleImageLoad}
              onError={handleImageError}
              style={{ 
                display: streamError ? 'none' : 'block',
                minHeight: '400px',
                maxHeight: '720px',
                backgroundColor: '#1f2937'
              }}
            />

            {/* Live Indicator Badge */}
            {streamStatus?.status === 'streaming' && !streamError && (
              <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1.5 rounded-full text-sm font-bold flex items-center space-x-2 shadow-lg">
                <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                <span>LIVE</span>
              </div>
            )}

            {/* Camera Info Badge */}
            {streamStatus?.status === 'streaming' && !streamError && (
              <div className="absolute top-4 right-4 bg-black bg-opacity-60 text-white px-3 py-1.5 rounded text-sm backdrop-blur-sm">
                {streamStatus.camera_name || `Camera ${cameraIndex}`}
              </div>
            )}

            {/* Bottom Info Bar */}
            {streamStatus?.status === 'streaming' && !streamError && (
              <div className="absolute bottom-4 left-4 right-4 bg-black bg-opacity-60 text-white px-4 py-2 rounded flex justify-between items-center text-sm backdrop-blur-sm">
                <div className="flex space-x-4">
                  <span>📊 {streamStatus.net_count} Net</span>
                  <span>⬇️ {streamStatus.entry_count} In</span>
                  <span>⬆️ {streamStatus.exit_count} Out</span>
                </div>
                <div>
                  <span>{streamStatus.fps?.toFixed(1)} FPS</span>
                </div>
              </div>
            )}
          </div>

          {/* Performance Tips */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <h3 className="font-semibold text-gray-700 mb-2 flex items-center">
              <AlertCircle className="w-4 h-4 mr-2 text-blue-600" />
              Performance Optimization
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div className="bg-blue-50 rounded p-3">
                <p className="font-medium text-blue-900">Frame Skipping</p>
                <p className="text-blue-700 text-xs mt-1">
                  Currently processing every {streamStatus?.config?.frame_skip || frameSkip} frame(s)
                </p>
              </div>
              <div className="bg-green-50 rounded p-3">
                <p className="font-medium text-green-900">Smooth Display</p>
                <p className="text-green-700 text-xs mt-1">
                  All frames shown, detection on skipped frames
                </p>
              </div>
              <div className="bg-purple-50 rounded p-3">
                <p className="font-medium text-purple-900">MJPEG Streaming</p>
                <p className="text-purple-700 text-xs mt-1">
                  Optimized multipart streaming prevents buffering
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Webcam;
