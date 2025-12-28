/**
 * CountBadge component - Displays entry/exit count badges
 */
const CountBadge = ({ label, count, type = 'default' }) => {
  const typeClasses = {
    default: 'bg-gray-100 text-gray-800',
    entry: 'bg-green-100 text-green-800',
    exit: 'bg-red-100 text-red-800',
    net: 'bg-blue-100 text-blue-800',
    total: 'bg-purple-100 text-purple-800',
  };

  return (
    <div className={`inline-flex items-center px-4 py-2 rounded-lg ${typeClasses[type]}`}>
      <span className="text-sm font-medium mr-2">{label}:</span>
      <span className="text-2xl font-bold">{count}</span>
    </div>
  );
};

export default CountBadge;
