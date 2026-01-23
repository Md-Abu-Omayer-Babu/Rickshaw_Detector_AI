/**
 * CCTV Monitoring Page - Real-time Continuous Streaming
 * Uses continuous streaming endpoints for live MJPEG video with real-time counts
 */
import { useState, useEffect, useRef } from 'react';
import { startCCTVStream, stopCCTVStream, getCCTVStatus, getCCTVStreamUrl, testStreamConnection } from '../api/client';
import Loader from '../components/Loader';
import { Camera, Video, VideoOff, Play, Square, Wifi, WifiOff, AlertCircle, CheckCircle } from 'lucide-react';

const CCTV = () => {
  // Form state
  const [cameraId, setCameraId] = useState('');
  const [rtspUrl, setRtspUrl] = useState('');
  const [cameraName, setCameraName] = useState('');
  
  // Stream state
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamStatus, setStreamStatus] = useState(null);
  const [streamError, setStreamError] = useState(false);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  
  // Refs
  const pollIntervalRef = useRef(null);
  const imgRef = useRef(null);

  // Poll stream status every 1.5 seconds
  useEffect(() => {
    if (!isStreaming || !cameraId) {
      return;
    }

    const fetchStatus = async () => {
      try {
        const data = await getCCTVStatus(cameraId);
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
        // Don't set error here to avoid interrupting the stream
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
  }, [isStreaming, cameraId]);

  const handleTestConnection = async () => {
    if (!cameraId || !rtspUrl) {
      setError('Please provide Camera ID and RTSP URL');
      return;
    }

    try {
      setTesting(true);
      setError(null);
      setSuccessMessage(null);
      setTestResult(null);
      const response = await testStreamConnection(cameraId, rtspUrl);
      setTestResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to test stream connection');
    } finally {
      setTesting(false);
    }
  };

  const handleStartStream = async () => {
    if (!cameraId || !rtspUrl) {
      setError('Please provide Camera ID and RTSP URL');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);
      setStreamError(false);
      
      const response = await startCCTVStream(cameraId, rtspUrl, cameraName);
      setIsStreaming(true);
      setSuccessMessage('Stream started successfully! Loading video...');
      
      console.log('Start Stream Response:', response);

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start stream');
      setIsStreaming(false);
    } finally {
      setLoading(false);
    }
  };

  const handleStopStream = async () => {
    if (!cameraId) {
      setError('Camera ID is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);
      
      await stopCCTVStream(cameraId);
      setIsStreaming(false);
      setStreamStatus(null);
      setSuccessMessage('Stream stopped successfully');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to stop stream');
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
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <Video className="w-6 h-6 text-blue-500 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-blue-800 font-medium">Real-time CCTV Streaming</p>
            <p className="text-blue-700 text-sm mt-1">
              Stream live RTSP feeds with real-time object detection and counting. 
              Start the stream to see live video with bounding boxes and entry/exit tracking.
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
        <div className="flex items-center mb-2">
          <Camera className="w-6 h-6 text-gray-700 mr-2" />
          <h2 className="text-2xl font-bold text-gray-800">Stream Configuration</h2>
        </div>
        <p className="text-gray-600 mb-6">
          Configure camera connection to start live streaming
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Camera ID <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={cameraId}
              onChange={(e) => setCameraId(e.target.value)}
              placeholder="e.g., camera_01"
              disabled={isStreaming}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <p className="text-xs text-gray-500 mt-1">
              Unique identifier for this camera
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              RTSP URL <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={rtspUrl}
              onChange={(e) => setRtspUrl(e.target.value)}
              placeholder="rtsp://username:password@192.168.1.100:554/stream1"
              disabled={isStreaming}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <p className="text-xs text-gray-500 mt-1">
              Format: rtsp://username:password@ip:port/path
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
              placeholder="e.g., Main Gate Camera"
              disabled={isStreaming}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4">
            <button
              onClick={handleTestConnection}
              disabled={testing || loading || isStreaming}
              className="flex-1 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center"
            >
              {testing ? (
                <>
                  <Loader size="small" className="mr-2" />
                  Testing...
                </>
              ) : (
                <>
                  <Wifi className="w-5 h-5 mr-2" />
                  Test Connection
                </>
              )}
            </button>
            
            {!isStreaming ? (
              <button
                onClick={handleStartStream}
                disabled={loading || testing}
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
                    Start Stream
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
                    Stop Stream
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Test Result */}
      {testResult && !isStreaming && (
        <div className={`rounded-lg p-6 ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <div className="flex items-start">
            {testResult.success ? (
              <CheckCircle className="w-6 h-6 text-green-500 mr-2 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-6 h-6 text-red-500 mr-2 flex-shrink-0" />
            )}
            <div className="flex-1">
              <p className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'}`}>
                {testResult.message}
              </p>
              {testResult.stream_properties && (
                <div className="mt-2 text-sm space-y-1">
                  <p className="text-green-700">
                    Resolution: {testResult.stream_properties.width} × {testResult.stream_properties.height}
                  </p>
                  <p className="text-green-700">
                    FPS: {testResult.stream_properties.fps}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Live Stream Viewer */}
      {isStreaming && cameraId && (
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
                        {streamStatus.camera_name || cameraId}
                      </p>
                    </div>
                  </>
                ) : streamStatus?.status === 'connecting' ? (
                  <>
                    <Loader size="small" className="mr-2" />
                    <span className="font-semibold text-gray-900">Connecting...</span>
                  </>
                ) : streamStatus?.status === 'stopped' ? (
                  <>
                    <WifiOff className="w-5 h-5 text-gray-600 mr-2" />
                    <span className="font-semibold text-gray-900">Stopped</span>
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
                    Uptime: <span className="font-medium">{Math.floor(streamStatus.uptime || 0)}s</span>
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
                  <p className="text-xs text-gray-600 mb-1">Frames</p>
                  <p className="text-xl font-bold text-gray-700">{streamStatus.frames_processed || 0}</p>
                </div>
              </div>
            )}

            {/* Stream Properties */}
            {streamStatus?.stream_properties && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                  Resolution: {streamStatus.stream_properties.width}×{streamStatus.stream_properties.height} @ {streamStatus.stream_properties.fps} FPS
                </p>
              </div>
            )}

            {/* Error Message in Status */}
            {streamStatus?.error_message && (
              <div className="mt-3 text-sm text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {streamStatus.error_message}
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
                    Waiting for stream connection...
                  </p>
                </div>
              </div>
            )}

            {/* MJPEG Stream */}
            <img
              ref={imgRef}
              src={getCCTVStreamUrl(cameraId)}
              alt={`Live CCTV Feed - ${cameraId}`}
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
                {streamStatus.camera_name || cameraId}
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

          {/* Stream Info Footer */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="flex items-center justify-between text-sm">
              <div className="text-gray-600">
                Camera ID: <span className="font-mono font-medium text-gray-900">{cameraId}</span>
              </div>
              {streamStatus?.status === 'stopped' && (
                <span className="text-red-600 flex items-center">
                  <VideoOff className="w-4 h-4 mr-1" />
                  Stream Stopped
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CCTV;
