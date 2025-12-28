/**
 * Image Detection Page - Upload and detect rickshaws in images
 */
import { useState } from 'react';
import { detectImage } from '../api/client';
import { getStaticUrl } from '../api/client';
import UploadBox from '../components/UploadBox';
import ImageViewer from '../components/ImageViewer';
import Loader from '../components/Loader';

const ImageDetection = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setResult(null);
    setError(null);
  };

  const handleDetection = async () => {
    if (!selectedFile) {
      setError('Please select an image file');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await detectImage(selectedFile);
      setResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process image');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Upload Image</h2>
        <p className="text-gray-600 mb-6">
          Upload an image to detect rickshaws. Supported formats: JPG, PNG, BMP, WEBP
        </p>

        <UploadBox
          onFileSelect={handleFileSelect}
          accept="image/*"
          maxSize={500 * 1024 * 1024}
          label="Upload Image"
        />

        {selectedFile && !result && (
          <div className="mt-6">
            <button
              onClick={handleDetection}
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium text-lg"
            >
              {loading ? 'Processing...' : 'Detect Rickshaws'}
            </button>
          </div>
        )}
      </div>

      {loading && (
        <div className="bg-white rounded-lg shadow-md p-8">
          <Loader size="large" message="Processing image... This may take a moment." />
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
                <p className="text-green-800 font-medium">Detection Complete!</p>
              </div>
              <button
                onClick={() => {
                  setResult(null);
                  setSelectedFile(null);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Process Another Image
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Detection Results</h3>
            <ImageViewer
              imageUrl={getStaticUrl(result.output_url)}
              rickshawCount={result.rickshaw_count}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageDetection;
