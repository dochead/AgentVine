import { useQuery } from '@tanstack/react-query';
import { getSessions, getTasks, getWorkers } from '../api';

export default function Sessions() {
  const { data: sessions, isLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: getSessions,
  });

  const { data: tasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: getTasks,
  });

  const { data: workers } = useQuery({
    queryKey: ['workers'],
    queryFn: getWorkers,
  });

  const getTaskTitle = (taskId?: string) => {
    if (!taskId || !tasks) return 'No task assigned';
    const task = tasks.find((t) => t.id === taskId);
    return task?.title || 'Unknown task';
  };

  const getWorkerName = (workerId: string) => {
    if (!workers) return 'Unknown worker';
    const worker = workers.find((w) => w.id === workerId);
    return worker?.name || 'Unknown worker';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'idle':
        return 'bg-yellow-100 text-yellow-800';
      case 'terminated':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getActivityStatus = (lastActivity: string) => {
    const now = new Date().getTime();
    const activityTime = new Date(lastActivity).getTime();
    const diffSeconds = Math.floor((now - activityTime) / 1000);

    if (diffSeconds < 60) return 'Active now';
    if (diffSeconds < 300) return `${Math.floor(diffSeconds / 60)}m ago`;
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)}m inactive`;
    return `${Math.floor(diffSeconds / 3600)}h inactive`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Sessions</h1>
        <div className="text-sm text-gray-500">
          Session ID ↔ Task mappings
        </div>
      </div>

      <div className="bg-white rounded-lg shadow mb-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Active Sessions</h2>
          <p className="text-sm text-gray-500 mt-1">
            Sessions maintain context for ongoing work
          </p>
        </div>
        {isLoading ? (
          <div className="px-6 py-8 text-center text-gray-500">Loading sessions...</div>
        ) : (
          <div className="divide-y divide-gray-200">
            {sessions
              ?.filter((s) => s.status === 'active')
              .map((session) => (
                <div key={session.id} className="px-6 py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm font-medium text-gray-900">
                          {session.session_id}
                        </span>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(session.status)}`}>
                          {session.status}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Worker:</span>
                          <p className="text-gray-900 font-medium">
                            {getWorkerName(session.worker_id)}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-500">Task:</span>
                          <p className="text-gray-900">{getTaskTitle(session.task_id)}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Created:</span>
                          <p className="text-gray-900">
                            {new Date(session.created_at).toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-500">Last Activity:</span>
                          <p className="text-gray-900">
                            {getActivityStatus(session.last_activity_at)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            {!sessions?.filter((s) => s.status === 'active').length ? (
              <div className="px-6 py-8 text-center text-gray-500">
                No active sessions
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* All Sessions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">All Sessions</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {sessions?.map((session) => (
            <div key={session.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-mono text-gray-900 truncate">
                    {session.session_id}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {getWorkerName(session.worker_id)} → {getTaskTitle(session.task_id)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {getActivityStatus(session.last_activity_at)}
                  </p>
                </div>
                <div className="ml-4 flex-shrink-0">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(session.status)}`}>
                    {session.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
          {!sessions || sessions.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              No sessions yet. Sessions are created when workers claim tasks.
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
