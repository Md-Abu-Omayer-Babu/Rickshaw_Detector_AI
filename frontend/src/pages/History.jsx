/**
 * History Page - View detection records with filtering and export options
 */
import { useEffect, useState } from 'react';
import { Calendar, Filter, FileText, Download, FileDown } from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { getHistory, exportLogs } from '../api/client';
import Loader from '../components/Loader';
import { formatDateTime, downloadFile } from '../utils/formatters';

const History = () => {
  // Data state
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);

  // Filter state
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    file_type: ''
  });
  const [appliedFilters, setAppliedFilters] = useState({});

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async (filterParams = {}) => {
    try {
      setLoading(true);
      setError(null);
      const result = await getHistory(filterParams);
      setData(result);
      setAppliedFilters(filterParams);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch history data');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleApplyFilters = () => {
    const filterParams = {};
    if (filters.start_date) filterParams.start_date = filters.start_date;
    if (filters.end_date) filterParams.end_date = filters.end_date;
    if (filters.file_type) filterParams.file_type = filters.file_type;
    
    fetchHistory(filterParams);
  };

  const handleResetFilters = () => {
    setFilters({
      start_date: '',
      end_date: '',
      file_type: ''
    });
    fetchHistory({});
  };

  const handleExportCSV = async () => {
    try {
      setExporting(true);
      const response = await exportLogs({ 
        format: 'csv',
        ...appliedFilters,
        limit: 10000 
      });
      
      downloadFile(
        response.data, 
        `rickshaw_history_${new Date().toISOString().split('T')[0]}.csv`
      );
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to export CSV');
    } finally {
      setExporting(false);
    }
  };

  const handleExportJSON = async () => {
    try {
      setExporting(true);
      const response = await exportLogs({ 
        format: 'json',
        ...appliedFilters,
        limit: 10000 
      });
      
      const blob = new Blob(
        [JSON.stringify(response.data, null, 2)], 
        { type: 'application/json' }
      );
      downloadFile(
        blob, 
        `rickshaw_history_${new Date().toISOString().split('T')[0]}.json`
      );
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to export JSON');
    } finally {
      setExporting(false);
    }
  };

  const handleExportPDF = () => {
    try {
      setExporting(true);
      
      const doc = new jsPDF();
      
      // Add header
      doc.setFontSize(18);
      doc.setFont('helvetica', 'bold');
      doc.text('Rickshaw Detection History', 14, 20);
      
      // Add export timestamp
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28);
      
      // Add filter info if applied
      let yPosition = 35;
      if (appliedFilters.start_date || appliedFilters.end_date || appliedFilters.file_type) {
        doc.setFontSize(9);
        doc.setTextColor(100);
        doc.text('Filters Applied:', 14, yPosition);
        yPosition += 5;
        
        if (appliedFilters.start_date) {
          doc.text(`  • Start Date: ${appliedFilters.start_date}`, 14, yPosition);
          yPosition += 5;
        }
        if (appliedFilters.end_date) {
          doc.text(`  • End Date: ${appliedFilters.end_date}`, 14, yPosition);
          yPosition += 5;
        }
        if (appliedFilters.file_type) {
          doc.text(`  • File Type: ${appliedFilters.file_type}`, 14, yPosition);
          yPosition += 5;
        }
        yPosition += 3;
      }
      
      // Add total records
      doc.setFontSize(10);
      doc.setTextColor(0);
      doc.text(`Total Records: ${data.total_records}`, 14, yPosition);
      
      // Prepare table data
      const tableData = data.detections.map(record => [
        record.id.toString(),
        record.file_type.toUpperCase(),
        record.file_name,
        record.rickshaw_count.toString(),
        formatDateTime(record.created_at)
      ]);
      
      // Add table
      doc.autoTable({
        head: [['ID', 'Type', 'File Name', 'Count', 'Date & Time']],
        body: tableData,
        startY: yPosition + 8,
        styles: {
          fontSize: 8,
          cellPadding: 3
        },
        headStyles: {
          fillColor: [59, 130, 246],
          fontStyle: 'bold'
        },
        alternateRowStyles: {
          fillColor: [245, 247, 250]
        },
        columnStyles: {
          0: { cellWidth: 15 },
          1: { cellWidth: 20 },
          2: { cellWidth: 70 },
          3: { cellWidth: 20, halign: 'center' },
          4: { cellWidth: 45 }
        }
      });
      
      // Save PDF
      doc.save(`rickshaw_history_${new Date().toISOString().split('T')[0]}.pdf`);
      
    } catch (err) {
      console.error('PDF export error:', err);
      setError('Failed to generate PDF');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader size="large" />
      </div>
    );
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
          onClick={() => fetchHistory(appliedFilters)}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) {
    return <div className="text-center text-gray-500 py-12">No history data available</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <FileText className="w-8 h-8 text-blue-600" />
            Detection History
          </h1>
          <p className="text-gray-600 mt-1">
            Total Records: <span className="font-semibold text-blue-600">{data.total_records}</span>
          </p>
        </div>
      </div>

      {/* Filters Card */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-700" />
          <h2 className="text-xl font-semibold text-gray-800">Filters</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Start Date */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Calendar className="w-4 h-4" />
              Start Date
            </label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange('start_date', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
          </div>

          {/* End Date */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Calendar className="w-4 h-4" />
              End Date
            </label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => handleFilterChange('end_date', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
          </div>

          {/* File Type */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <FileText className="w-4 h-4" />
              File Type
            </label>
            <select
              value={filters.file_type}
              onChange={(e) => handleFilterChange('file_type', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors bg-white"
            >
              <option value="">All Types</option>
              <option value="image">Image</option>
              <option value="video">Video</option>
            </select>
          </div>

          {/* Filter Buttons */}
          <div className="flex items-end gap-2">
            <button
              onClick={handleApplyFilters}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Apply
            </button>
            <button
              onClick={handleResetFilters}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Export Buttons */}
      <div className="flex gap-3 justify-end">
        <button
          onClick={handleExportPDF}
          disabled={exporting || data.detections.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors shadow-md"
        >
          <FileDown className="w-4 h-4" />
          {exporting ? 'Exporting...' : 'Export PDF'}
        </button>
        <button
          onClick={handleExportCSV}
          disabled={exporting || data.detections.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors shadow-md"
        >
          <Download className="w-4 h-4" />
          {exporting ? 'Exporting...' : 'Export CSV'}
        </button>
        <button
          onClick={handleExportJSON}
          disabled={exporting || data.detections.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors shadow-md"
        >
          <Download className="w-4 h-4" />
          {exporting ? 'Exporting...' : 'Export JSON'}
        </button>
      </div>

      {/* Records Table */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        {data.detections.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <svg className="w-20 h-20 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-lg font-medium text-gray-600 mb-2">No detection records found</p>
            <p className="text-sm text-gray-500">Try adjusting your filters or upload some files to detect</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
                <tr>
                  <th className="text-left py-4 px-6 font-semibold">ID</th>
                  <th className="text-left py-4 px-6 font-semibold">File Type</th>
                  <th className="text-left py-4 px-6 font-semibold">File Name</th>
                  <th className="text-center py-4 px-6 font-semibold">Rickshaw Count</th>
                  <th className="text-left py-4 px-6 font-semibold">Date & Time</th>
                </tr>
              </thead>
              <tbody>
                {data.detections.map((record, index) => (
                  <tr
                    key={record.id}
                    className={`border-b hover:bg-blue-50 transition-colors ${
                      index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                    }`}
                  >
                    <td className="py-4 px-6 text-gray-900 font-medium">{record.id}</td>
                    <td className="py-4 px-6">
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                          record.file_type === 'image'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-purple-100 text-purple-800'
                        }`}
                      >
                        {record.file_type === 'image' ? (
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        )}
                        {record.file_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-gray-900 font-mono text-sm truncate max-w-xs" title={record.file_name}>
                      {record.file_name}
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100 text-green-800 font-bold text-lg">
                        {record.rickshaw_count}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-gray-600">
                      {formatDateTime(record.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
