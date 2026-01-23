import { useState } from 'react';
import LiveVideoPreview from './LiveVideoPreview';
import axios from 'axios';

/**
 * Example usage of LiveVideoPreview component
 */
const VideoProcessingPage = () => {
  const [jobId, setJobId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [results, setResults] = useState(null);

  const handleVideoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Upload video and get job ID
      const response = await axios.post(
        'http://localhost:8000/api/detect/video/async',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setJobId(response.data.job_id);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload video: ' + error.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcessingComplete = (data) => {
    console.log('Processing complete:', data);
    setResults(data);
  };

  const handleProcessingError = (error) => {
    console.error('Processing error:', error);
    alert('Processing failed: ' + error);
  };

  const resetUpload = () => {
    setJobId(null);
    setResults(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          Video Processing with Live Preview
        </h1>

        {/* Upload Section */}
        {!jobId && (
          <div className="bg-white rounded-lg shadow-md p-8 max-w-xl mx-auto">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Upload Video
            </h2>
            <input
              type="file"
              accept="video/*"
              onChange={handleVideoUpload}
              disabled={isUploading}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
                disabled:opacity-50 disabled:cursor-not-allowed"
            />
            {isUploading && (
              <p className="mt-3 text-sm text-gray-600">Uploading video...</p>
            )}
          </div>
        )}

        {/* Live Preview Section */}
        {jobId && (
          <div>
            <LiveVideoPreview
              jobId={jobId}
              onComplete={handleProcessingComplete}
              onError={handleProcessingError}
            />

            {/* Results Section */}
            {results && (
              <div className="mt-6 bg-white rounded-lg shadow-md p-6 max-w-4xl mx-auto">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">
                  Processing Results
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Total Entries</p>
                    <p className="text-2xl font-bold text-green-600">
                      {results.entry_count || 0}
                    </p>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Total Exits</p>
                    <p className="text-2xl font-bold text-red-600">
                      {results.exit_count || 0}
                    </p>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Detections</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {results.detections || 0}
                    </p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Duration</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {results.duration ? `${results.duration.toFixed(1)}s` : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Reset Button */}
            <div className="mt-6 text-center">
              <button
                onClick={resetUpload}
                className="px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Process Another Video
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoProcessingPage;
