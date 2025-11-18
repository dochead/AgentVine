import { useQuery } from '@tanstack/react-query';
import { getWorkers } from '../api';

export default function Workers() {
  const { data: workers, isLoading } = useQuery({
    queryKey: ['workers'],
    queryFn: getWorkers,
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'bg-green-100 text-green-800';
      case 'busy':
        return 'bg-yellow-100 text-yellow-800';
      case 'waiting':
        return 'bg-blue-100 text-blue-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'offline':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getHeartbeatStatus = (lastHeartbeat?: string) => {
    if (!lastHeartbeat) return 'Never';

    const now = new Date().getTime();
    const heartbeatTime = new Date(lastHeartbeat).getTime();
    const diffSeconds = Math.floor((now - heartbeatTime) / 1000);

    if (diffSeconds < 60) return 'Just now';
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}m ago`;
    return `${Math.floor(diffSeconds / 3600)}h ago`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Workers</h1>
        <div className="text-sm text-gray-500">
          Auto-refreshing every 3 seconds
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Registered Workers</h2>
        </div>
        {isLoading ? (
          <div className="px-6 py-8 text-center text-gray-500">Loading workers...</div>
        ) : (
          <div className="divide-y divide-gray-200">
            {workers?.map((worker) => (
              <div key={worker.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <p className="text-sm font-medium text-gray-900">{worker.name}</p>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(worker.status)}`}>
                        {worker.status}
                      </span>
                    </div>
                    <div className="mt-2 grid grid-cols-3 gap-4 text-xs text-gray-500">
                      <div>
                        <span className="font-medium">Worker ID:</span>
                        <p className="mt-1 font-mono">{worker.id.substring(0, 8)}...</p>
                      </div>
                      <div>
                        <span className="font-medium">Last Heartbeat:</span>
                        <p className="mt-1">{getHeartbeatStatus(worker.last_heartbeat_at)}</p>
                      </div>
                      <div>
                        <span className="font-medium">Registered:</span>
                        <p className="mt-1">{new Date(worker.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {!workers || workers.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                No workers registered. Start workers with <code className="bg-gray-100 px-2 py-1 rounded">docker compose up</code>
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* Worker Statistics */}
      {workers && workers.length > 0 && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-600 mb-2">Idle Workers</div>
            <div className="text-3xl font-bold text-green-600">
              {workers.filter((w) => w.status === 'idle').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-600 mb-2">Busy Workers</div>
            <div className="text-3xl font-bold text-yellow-600">
              {workers.filter((w) => w.status === 'busy').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm font-medium text-gray-600 mb-2">Error/Offline</div>
            <div className="text-3xl font-bold text-red-600">
              {workers.filter((w) => w.status === 'error' || w.status === 'offline').length}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
