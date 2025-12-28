/**
 * CCTV Monitoring Page - Process RTSP streams
 * NOTE: Backend uses blocking processing, not real-time streaming
 */
import { useState } from 'react';
import { processCCTVStream, testStreamConnection } from '../api/client';
import Loader from '../components/Loader';

const CCTV = () => {
  const [cameraId, setCameraId] = useState('');
  const [rtspUrl, setRtspUrl] = useState('');
  const [duration, setDuration] = useState(60);
  const [cameraName, setCameraName] = useState('');
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [error, setError] = useState(null);

  const handleTestConnection = async () => {
    if (!cameraId || !rtspUrl) {
      setError('Please provide Camera ID and RTSP URL');
      return;
    }

    try {
      setTesting(true);
      setError(null);
      setTestResult(null);
      const response = await testStreamConnection(cameraId, rtspUrl);
      setTestResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to test stream connection');
    } finally {
      setTesting(false);
    }
  };

  const handleProcessStream = async () => {
    if (!cameraId || !rtspUrl) {
      setError('Please provide Camera ID and RTSP URL');
      return;
    }

    if (duration < 1 || duration > 3600) {
      setError('Duration must be between 1 and 3600 seconds');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);
      const response = await processCCTVStream(cameraId, rtspUrl, duration, cameraName);
      setResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process CCTV stream');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Information Banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-6 h-6 text-blue-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p className="text-blue-800 font-medium">CCTV Stream Processing</p>
            <p className="text-blue-700 text-sm mt-1">
              This feature processes the RTSP stream for a specified duration and returns the total counts. 
              It does NOT provide real-time live streaming. For continuous monitoring, you'll need to run 
              multiple processing sessions.
            </p>
          </div>
        </div>
      </div>

      {/* Configuration Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">CCTV Stream Configuration</h2>
        <p className="text-gray-600 mb-6">
          Configure and process RTSP stream from CCTV cameras
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
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            />
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
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Processing Duration (seconds)
            </label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              min="1"
              max="3600"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Duration to process the stream (1-3600 seconds)
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4">
            <button
              onClick={handleTestConnection}
              disabled={testing || loading}
              className="flex-1 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {testing ? 'Testing...' : 'Test Connection'}
            </button>
            <button
              onClick={handleProcessStream}
              disabled={loading || testing}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Processing...' : 'Start Processing'}
            </button>
          </div>
        </div>
      </div>

      {/* Test Result */}
      {testResult && (
        <div className={`rounded-lg p-6 ${testResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <div className="flex items-start">
            <svg className={`w-6 h-6 mr-2 flex-shrink-0 ${testResult.success ? 'text-green-500' : 'text-red-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={testResult.success ? "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" : "M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"} />
            </svg>
            <div className="flex-1">
              <p className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'}`}>
                {testResult.message}
              </p>
              {testResult.stream_properties && (
                <div className="mt-2 text-sm">
                  <p className="text-green-700">
                    Resolution: {testResult.stream_properties.width} x {testResult.stream_properties.height}
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

      {/* Loading State */}
      {loading && (
        <div className="bg-white rounded-lg shadow-md p-8">
          <Loader size="large" message={`Processing stream for ${duration} seconds...`} />
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              This will take approximately {duration} seconds. Please wait...
            </p>
          </div>
        </div>
      )}

      {/* Error Message */}
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

      {/* Processing Result */}
      {result && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <svg className="w-6 h-6 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-green-800 font-medium">Stream Processing Complete!</p>
              </div>
              <button
                onClick={() => setResult(null)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Process Again
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Processing Results</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600">Camera ID</p>
                <p className="text-lg font-bold text-purple-600">{result.camera_id}</p>
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
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-600">Frames Processed</p>
                <p className="text-2xl font-bold text-gray-600">{result.frames_processed}</p>
              </div>
            </div>

            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                Processing Duration: <span className="font-semibold">{result.duration.toFixed(2)}s</span>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CCTV;
