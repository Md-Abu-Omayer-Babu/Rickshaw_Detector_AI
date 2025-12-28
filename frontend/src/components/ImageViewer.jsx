/**
 * ImageViewer component - Displays processed images with annotations
 */
import { useState } from 'react';

const ImageViewer = ({ imageUrl, alt = 'Processed image', rickshawCount }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const handleImageLoad = () => {
    setLoading(false);
    setError(false);
  };

  const handleImageError = () => {
    setLoading(false);
    setError(true);
  };

  if (!imageUrl) {
    return (
      <div className="bg-gray-100 rounded-lg p-8 text-center">
        <p className="text-gray-500">No image to display</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {rickshawCount !== undefined && (
        <div className="bg-blue-600 text-white px-4 py-2">
          <p className="text-sm font-medium">
            Detected Rickshaws: <span className="text-xl font-bold">{rickshawCount}</span>
          </p>
        </div>
      )}

      <div className="relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent" />
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            <div className="text-center p-8">
              <svg
                className="w-16 h-16 text-red-500 mx-auto mb-4"
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
              <p className="text-gray-600">Failed to load image</p>
            </div>
          </div>
        )}

        <img
          src={imageUrl}
          alt={alt}
          onLoad={handleImageLoad}
          onError={handleImageError}
          className={`w-full h-auto ${loading ? 'invisible' : 'visible'}`}
        />
      </div>

      <div className="p-4 bg-gray-50">
        <a
          href={imageUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Open in new tab →
        </a>
      </div>
    </div>
  );
};

export default ImageViewer;
