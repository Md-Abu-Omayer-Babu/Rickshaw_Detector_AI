/**
 * VideoPlayer component - Plays processed videos with controls
 */
import { useState, useRef } from 'react';

const VideoPlayer = ({ videoUrl, entryCount, exitCount, netCount }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const videoRef = useRef(null);

  const handleVideoLoad = () => {
    setLoading(false);
    setError(false);
  };

  const handleVideoError = () => {
    setLoading(false);
    setError(true);
  };

  if (!videoUrl) {
    return (
      <div className="bg-gray-100 rounded-lg p-8 text-center">
        <p className="text-gray-500">No video to display</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Count badges */}
      {(entryCount !== undefined || exitCount !== undefined) && (
        <div className="bg-gray-800 text-white px-4 py-3 flex gap-4">
          {entryCount !== undefined && (
            <div className="flex items-center">
              <span className="text-sm font-medium mr-2">Entry:</span>
              <span className="text-xl font-bold text-green-400">{entryCount}</span>
            </div>
          )}
          {exitCount !== undefined && (
            <div className="flex items-center">
              <span className="text-sm font-medium mr-2">Exit:</span>
              <span className="text-xl font-bold text-red-400">{exitCount}</span>
            </div>
          )}
          {netCount !== undefined && (
            <div className="flex items-center">
              <span className="text-sm font-medium mr-2">Net:</span>
              <span className="text-xl font-bold text-blue-400">{netCount}</span>
            </div>
          )}
        </div>
      )}

      <div className="relative bg-black">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent" />
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
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
              <p className="text-white">Failed to load video</p>
            </div>
          </div>
        )}

        <video
          ref={videoRef}
          src={videoUrl}
          controls
          autoPlay
          onLoadedData={handleVideoLoad}
          onError={handleVideoError}
          className="w-full h-auto"
        >
          Your browser does not support the video tag.
        </video>
      </div>

      <div className="p-4 bg-gray-50">
        <a
          href={videoUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Download video →
        </a>
      </div>
    </div>
  );
};

export default VideoPlayer;
