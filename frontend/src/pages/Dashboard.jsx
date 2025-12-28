/**
 * Dashboard Page - Overview statistics and analytics
 */
import { useEffect, useState } from 'react';
import { getDashboardAnalytics } from '../api/client';
import StatCard from '../components/StatCard';
import Loader from '../components/Loader';
import { formatNumber } from '../utils/formatters';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cameraId, setCameraId] = useState('default');

  useEffect(() => {
    fetchDashboard();
  }, [cameraId]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await getDashboardAnalytics(cameraId);
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loader message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <svg className="w-6 h-6 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-800">{error}</p>
        </div>
        <button
          onClick={fetchDashboard}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) {
    return <div className="text-center text-gray-500">No data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header with camera selector */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard Overview</h1>
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Camera:</label>
          <select
            value={cameraId}
            onChange={(e) => setCameraId(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="default">Default</option>
            <option value="all">All Cameras</option>
          </select>
        </div>
      </div>

      {/* All Time Stats */}
      <div>
        <h2 className="text-xl font-semibold text-gray-700 mb-4">All Time Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Total Entry"
            value={formatNumber(data.total_entry)}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
            }
            color="green"
          />
          <StatCard
            title="Total Exit"
            value={formatNumber(data.total_exit)}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            }
            color="red"
          />
          <StatCard
            title="Net Count"
            value={formatNumber(data.net_count)}
            subtitle={data.net_count >= 0 ? 'More entries' : 'More exits'}
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
            color="blue"
          />
        </div>
      </div>

      {/* Today's Stats */}
      <div>
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Today's Activity</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Today's Entry"
            value={formatNumber(data.today_entry)}
            color="green"
          />
          <StatCard
            title="Today's Exit"
            value={formatNumber(data.today_exit)}
            color="red"
          />
          <StatCard
            title="Today's Net"
            value={formatNumber(data.today_net)}
            color="blue"
          />
        </div>
      </div>

      {/* Peak Hour Info */}
      {data.peak_hour && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Peak Hour Today</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-600">Peak Hour</p>
              <p className="text-2xl font-bold text-purple-600">
                {data.peak_hour.hour}:00
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Entry</p>
              <p className="text-2xl font-bold text-green-600">
                {data.peak_hour.entry_count}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Exit</p>
              <p className="text-2xl font-bold text-red-600">
                {data.peak_hour.exit_count}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-2xl font-bold text-blue-600">
                {data.peak_hour.total_count}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Daily Trend */}
      {data.daily_trend && data.daily_trend.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">7-Day Trend</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4">Date</th>
                  <th className="text-right py-2 px-4">Entry</th>
                  <th className="text-right py-2 px-4">Exit</th>
                  <th className="text-right py-2 px-4">Net</th>
                </tr>
              </thead>
              <tbody>
                {data.daily_trend.map((day, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="py-2 px-4">{day.date}</td>
                    <td className="text-right py-2 px-4 text-green-600 font-medium">
                      {formatNumber(day.entry_count)}
                    </td>
                    <td className="text-right py-2 px-4 text-red-600 font-medium">
                      {formatNumber(day.exit_count)}
                    </td>
                    <td className="text-right py-2 px-4 text-blue-600 font-medium">
                      {formatNumber(day.net_count)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
