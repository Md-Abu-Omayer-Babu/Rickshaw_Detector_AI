/**
 * Analytics Page - Charts and visualizations
 */
import { useEffect, useState } from 'react';
import { getDashboardAnalytics } from '../api/client';
import Loader from '../components/Loader';
import { formatNumber, formatHour } from '../utils/formatters';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const Analytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cameraId, setCameraId] = useState('default');

  useEffect(() => {
    fetchAnalytics();
  }, [cameraId]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await getDashboardAnalytics(cameraId);
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loader message="Loading analytics..." />;
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
          onClick={fetchAnalytics}
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

  // Prepare data for daily trend chart
  const dailyChartData = data.daily_trend?.map(day => ({
    date: day.date,
    Entry: day.entry_count,
    Exit: day.exit_count,
    Net: day.net_count,
  })) || [];

  // Prepare data for hourly distribution
  const hourlyMap = {};
  data.hourly_distribution?.forEach(item => {
    const hour = parseInt(item.hour);
    if (!hourlyMap[hour]) {
      hourlyMap[hour] = { hour: formatHour(hour), Entry: 0, Exit: 0 };
    }
    if (item.event_type === 'entry') {
      hourlyMap[hour].Entry = item.count;
    } else if (item.event_type === 'exit') {
      hourlyMap[hour].Exit = item.count;
    }
  });
  const hourlyChartData = Object.values(hourlyMap);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-800">Analytics & Reports</h1>
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

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Total Entry</p>
              <p className="text-4xl font-bold mt-2">{formatNumber(data.total_entry)}</p>
            </div>
            <svg className="w-12 h-12 text-green-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm font-medium">Total Exit</p>
              <p className="text-4xl font-bold mt-2">{formatNumber(data.total_exit)}</p>
            </div>
            <svg className="w-12 h-12 text-red-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Net Count</p>
              <p className="text-4xl font-bold mt-2">{formatNumber(data.net_count)}</p>
            </div>
            <svg className="w-12 h-12 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Peak Hour Info */}
      {data.peak_hour && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Peak Hour Today</h2>
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Time</p>
                <p className="text-3xl font-bold text-purple-600">
                  {data.peak_hour.hour}:00
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Entry</p>
                <p className="text-3xl font-bold text-green-600">
                  {data.peak_hour.entry_count}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Exit</p>
                <p className="text-3xl font-bold text-red-600">
                  {data.peak_hour.exit_count}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Total</p>
                <p className="text-3xl font-bold text-blue-600">
                  {data.peak_hour.total_count}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Daily Trend Chart */}
      {dailyChartData.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">7-Day Trend Analysis</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dailyChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="Entry" stroke="#10b981" strokeWidth={2} />
              <Line type="monotone" dataKey="Exit" stroke="#ef4444" strokeWidth={2} />
              <Line type="monotone" dataKey="Net" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Hourly Distribution Chart */}
      {hourlyChartData.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Today's Hourly Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hourlyChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="Entry" fill="#10b981" />
              <Bar dataKey="Exit" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Today vs All Time Comparison */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Today vs All Time</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">Today</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Entry:</span>
                <span className="font-bold text-green-600">{formatNumber(data.today_entry)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Exit:</span>
                <span className="font-bold text-red-600">{formatNumber(data.today_exit)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Net:</span>
                <span className="font-bold text-blue-600">{formatNumber(data.today_net)}</span>
              </div>
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-700 mb-3">All Time</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Entry:</span>
                <span className="font-bold text-green-600">{formatNumber(data.total_entry)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Exit:</span>
                <span className="font-bold text-red-600">{formatNumber(data.total_exit)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Net:</span>
                <span className="font-bold text-blue-600">{formatNumber(data.net_count)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
