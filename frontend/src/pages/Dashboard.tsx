import { useQuery } from '@tanstack/react-query';
import { getTasks, getWorkers, getSessions, getQueueStats } from '../api';

export default function Dashboard() {
  const { data: tasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: getTasks,
  });

  const { data: workers } = useQuery({
    queryKey: ['workers'],
    queryFn: getWorkers,
  });

  const { data: sessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: getSessions,
  });

  const { data: queueStats } = useQuery({
    queryKey: ['queueStats'],
    queryFn: getQueueStats,
  });

  const tasksByStatus = tasks?.reduce((acc, task) => {
    acc[task.status] = (acc[task.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const workersByStatus = workers?.reduce((acc, worker) => {
    acc[worker.status] = (acc[worker.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const totalQueueDepth = queueStats
    ? queueStats.high_priority.pending +
      queueStats.default.pending +
      queueStats.low_priority.pending
    : 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">Total Tasks</div>
          <div className="text-3xl font-bold text-gray-900">{tasks?.length || 0}</div>
          <div className="mt-2 text-sm text-gray-500">
            {tasksByStatus?.in_progress || 0} in progress
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">Active Workers</div>
          <div className="text-3xl font-bold text-gray-900">{workers?.length || 0}</div>
          <div className="mt-2 text-sm text-gray-500">
            {workersByStatus?.busy || 0} busy, {workersByStatus?.idle || 0} idle
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">Queue Depth</div>
          <div className="text-3xl font-bold text-gray-900">{totalQueueDepth}</div>
          <div className="mt-2 text-sm text-gray-500">
            {queueStats?.high_priority.pending || 0} high priority
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600 mb-1">Active Sessions</div>
          <div className="text-3xl font-bold text-gray-900">
            {sessions?.filter((s) => s.status === 'active').length || 0}
          </div>
          <div className="mt-2 text-sm text-gray-500">
            {sessions?.length || 0} total
          </div>
        </div>
      </div>

      {/* Recent Tasks */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Tasks</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {tasks?.slice(0, 5).map((task) => (
            <div key={task.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {task.title}
                  </p>
                  <p className="text-sm text-gray-500">{task.task_type}</p>
                </div>
                <div className="ml-4 flex-shrink-0">
                  <span
                    className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      task.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : task.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-800'
                        : task.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {task.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
          {!tasks || tasks.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              No tasks yet. Create your first task!
            </div>
          ) : null}
        </div>
      </div>

      {/* Workers Status */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Workers</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {workers?.map((worker) => (
            <div key={worker.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{worker.name}</p>
                  <p className="text-xs text-gray-500">
                    Last heartbeat:{' '}
                    {worker.last_heartbeat_at
                      ? new Date(worker.last_heartbeat_at).toLocaleTimeString()
                      : 'never'}
                  </p>
                </div>
                <span
                  className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    worker.status === 'busy'
                      ? 'bg-yellow-100 text-yellow-800'
                      : worker.status === 'idle'
                      ? 'bg-green-100 text-green-800'
                      : worker.status === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {worker.status}
                </span>
              </div>
            </div>
          ))}
          {!workers || workers.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              No workers registered
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
