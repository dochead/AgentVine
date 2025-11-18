import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Workers from './pages/Workers';
import Sessions from './pages/Sessions';
import Chat from './pages/Chat';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchInterval: 3000, // Poll every 3 seconds
      refetchIntervalInBackground: true,
      staleTime: 2000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex space-x-8">
                  <Link
                    to="/"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 border-b-2 border-transparent hover:border-gray-300"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/tasks"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 border-b-2 border-transparent hover:border-gray-300"
                  >
                    Tasks
                  </Link>
                  <Link
                    to="/workers"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 border-b-2 border-transparent hover:border-gray-300"
                  >
                    Workers
                  </Link>
                  <Link
                    to="/sessions"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 border-b-2 border-transparent hover:border-gray-300"
                  >
                    Sessions
                  </Link>
                  <Link
                    to="/chat"
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 border-b-2 border-transparent hover:border-gray-300"
                  >
                    Chat
                  </Link>
                </div>
                <div className="flex items-center">
                  <span className="text-xl font-bold text-gray-900">AgentVine</span>
                </div>
              </div>
            </div>
          </nav>

          <main>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/tasks" element={<Tasks />} />
              <Route path="/workers" element={<Workers />} />
              <Route path="/sessions" element={<Sessions />} />
              <Route path="/chat" element={<Chat />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
