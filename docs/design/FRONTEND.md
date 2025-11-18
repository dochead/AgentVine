# Frontend Design

## Overview

The AgentVine frontend is a React-based web application providing a real-time chat interface for monitoring workers, managing tasks, and interacting with the orchestration system.

## Technology Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS 4** - Styling
- **Shad.cn** - Component library
- **TanStack Query** - Data fetching and caching
- **Zustand** - Global state management
- **React Router 7** - Client-side routing
- **Socket.IO Client** - WebSocket communication
- **Zod** - Runtime validation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend App                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   App Router                         │  │
│  │  /             - Dashboard                           │  │
│  │  /chat         - Chat Interface                      │  │
│  │  /tasks        - Task Management                     │  │
│  │  /workers      - Worker Status                       │  │
│  │  /context      - Context Documents                   │  │
│  │  /settings     - Settings                            │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                         │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │              Page Components                         │  │
│  │  - DashboardPage                                     │  │
│  │  - ChatPage                                          │  │
│  │  - TasksPage                                         │  │
│  │  - WorkersPage                                       │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                         │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │          Feature Components                          │  │
│  │  - ChatWindow                                        │  │
│  │  - TaskList                                          │  │
│  │  - WorkerGrid                                        │  │
│  │  - ContextViewer                                     │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                         │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │           Shared Components                          │  │
│  │  (from Shad.cn)                                      │  │
│  │  - Button, Card, Dialog, Table, etc.                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              State Management                        │  │
│  │  - Zustand stores (auth, ui, realtime)              │  │
│  │  - TanStack Query cache                             │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               │                                             │
│  ┌────────────▼─────────────────────────────────────────┐  │
│  │              Services Layer                          │  │
│  │  - API Client (REST)                                 │  │
│  │  - WebSocket Client                                  │  │
│  │  - Auth Service                                      │  │
│  └────────────┬─────────────────────────────────────────┘  │
└───────────────┼──────────────────────────────────────────────┘
                │
                ▼
         ┌────────────┐
         │   Backend  │
         │    API     │
         └────────────┘
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # Shad.cn components
│   │   ├── chat/           # Chat-related components
│   │   ├── tasks/          # Task-related components
│   │   ├── workers/        # Worker-related components
│   │   └── shared/         # Shared components
│   │
│   ├── pages/              # Page components
│   │   ├── DashboardPage.tsx
│   │   ├── ChatPage.tsx
│   │   ├── TasksPage.tsx
│   │   ├── WorkersPage.tsx
│   │   ├── ContextPage.tsx
│   │   └── SettingsPage.tsx
│   │
│   ├── services/           # API and services
│   │   ├── api.ts          # REST API client
│   │   ├── websocket.ts    # WebSocket client
│   │   ├── auth.ts         # Authentication
│   │   └── storage.ts      # Local storage
│   │
│   ├── stores/             # Zustand stores
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   └── realtimeStore.ts
│   │
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useWebSocket.ts
│   │   ├── useTasks.ts
│   │   └── useWorkers.ts
│   │
│   ├── types/              # TypeScript types
│   │   ├── api.ts
│   │   ├── models.ts
│   │   └── events.ts
│   │
│   ├── utils/              # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   ├── App.tsx             # Root component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
│
├── public/                 # Static assets
├── tests/                  # Test files
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies
```

## Key Pages

### 1. Dashboard Page

**Purpose**: Overview of system status, active workers, and recent tasks

**Components**:
- System metrics (workers active, tasks in queue, completion rate)
- Recent activity timeline
- Queue status visualization
- Quick action buttons

```tsx
export function DashboardPage() {
  const { data: stats } = useQuery({
    queryKey: ['queue-stats'],
    queryFn: () => api.get('/api/v1/queue/status'),
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-6">
      <h1>Dashboard</h1>

      <MetricsGrid stats={stats} />
      <QueueStatusChart stats={stats} />
      <RecentActivityTimeline />
      <QuickActions />
    </div>
  );
}
```

### 2. Chat Page

**Purpose**: Real-time chat interface for worker communication

**Components**:
- Message list with streaming
- Input box with markdown support
- Worker request indicators
- Context viewer sidebar

```tsx
export function ChatPage() {
  const { conversationId } = useParams();
  const { messages, sendMessage } = useWebSocket(conversationId);
  const [input, setInput] = useState('');

  const handleSend = () => {
    sendMessage(input);
    setInput('');
  };

  return (
    <div className="flex h-screen">
      <div className="flex-1 flex flex-col">
        <ChatHeader conversationId={conversationId} />
        <MessageList messages={messages} />
        <ChatInput
          value={input}
          onChange={setInput}
          onSend={handleSend}
        />
      </div>

      <ContextSidebar conversationId={conversationId} />
    </div>
  );
}
```

### 3. Tasks Page

**Purpose**: Task management and monitoring

**Components**:
- Task list with filtering
- Task detail view
- Task creation form
- Status updates

```tsx
export function TasksPage() {
  const [filters, setFilters] = useState({
    status: 'all',
    type: 'all',
    priority: 'all',
  });

  const { data: tasks } = useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => api.get('/api/v1/tasks', { params: filters }),
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <h1>Tasks</h1>
        <CreateTaskButton />
      </div>

      <TaskFilters filters={filters} onChange={setFilters} />
      <TaskTable tasks={tasks?.items || []} />
    </div>
  );
}
```

### 4. Workers Page

**Purpose**: Worker status and management

**Components**:
- Worker grid with status
- Worker details modal
- Health metrics
- Activity logs

```tsx
export function WorkersPage() {
  const { data: workers } = useQuery({
    queryKey: ['workers'],
    queryFn: () => api.get('/api/v1/workers'),
    refetchInterval: 10000,
  });

  return (
    <div className="space-y-6">
      <h1>Workers</h1>

      <WorkerStats workers={workers?.items || []} />
      <WorkerGrid workers={workers?.items || []} />
    </div>
  );
}
```

## Component Library (Shad.cn)

### Installation

```bash
npx shadcn@latest init
```

### Core Components

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add table
npx shadcn@latest add form
npx shadcn@latest add input
npx shadcn@latest add select
npx shadcn@latest add badge
npx shadcn@latest add toast
npx shadcn@latest add dropdown-menu
npx shadcn@latest add tabs
npx shadcn@latest add scroll-area
npx shadcn@latest add separator
```

## State Management

### Zustand Stores

#### Auth Store

```tsx
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,

      login: async (username, password) => {
        const response = await api.post('/api/v1/auth/login', {
          username,
          password,
        });

        set({
          user: response.data.user,
          token: response.data.access_token,
        });
      },

      logout: () => {
        set({ user: null, token: null });
      },

      isAuthenticated: () => {
        return !!get().token;
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

#### UI Store

```tsx
interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  theme: 'light',

  toggleSidebar: () => set((state) => ({
    sidebarOpen: !state.sidebarOpen
  })),

  setTheme: (theme) => set({ theme }),
}));
```

## API Integration

### REST API Client

```tsx
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

// Request interceptor (add auth token)
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle errors)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### TanStack Query Setup

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router />
      <ReactQueryDevtools />
    </QueryClientProvider>
  );
}
```

## WebSocket Integration

```tsx
import { io, Socket } from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;
  private listeners: Map<string, Function[]> = new Map();

  connect(conversationId: string, token: string) {
    this.socket = io(`${API_URL}/chat/ws/${conversationId}`, {
      auth: { token },
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('message', (data) => {
      this.emit('message', data);
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });
  }

  disconnect() {
    this.socket?.disconnect();
    this.socket = null;
  }

  sendMessage(content: string) {
    this.socket?.emit('message', { content });
  }

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  off(event: string, callback: Function) {
    const listeners = this.listeners.get(event) || [];
    const index = listeners.indexOf(callback);
    if (index !== -1) {
      listeners.splice(index, 1);
    }
  }

  private emit(event: string, data: any) {
    const listeners = this.listeners.get(event) || [];
    listeners.forEach((callback) => callback(data));
  }
}

export const wsService = new WebSocketService();
```

### Custom Hook

```tsx
export function useWebSocket(conversationId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    if (!conversationId || !token) return;

    wsService.connect(conversationId, token);
    setIsConnected(true);

    wsService.on('message', (message: Message) => {
      setMessages((prev) => [...prev, message]);
    });

    return () => {
      wsService.disconnect();
      setIsConnected(false);
    };
  }, [conversationId, token]);

  const sendMessage = (content: string) => {
    wsService.sendMessage(content);
  };

  return { messages, sendMessage, isConnected };
}
```

## Chat Components

### MessageList

```tsx
interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <ScrollArea className="flex-1 p-4">
      <div className="space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={scrollRef} />
      </div>
    </ScrollArea>
  );
}
```

### MessageBubble

```tsx
interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isWorker = message.sender_type === 'worker';
  const isUser = message.sender_type === 'user';

  return (
    <div className={cn(
      'flex',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={cn(
        'max-w-[80%] rounded-lg p-4',
        isWorker && 'bg-blue-100',
        isUser && 'bg-green-100',
      )}>
        <div className="flex items-center gap-2 mb-2">
          <Badge>{message.sender_type}</Badge>
          <span className="text-xs text-gray-500">
            {formatTime(message.created_at)}
          </span>
        </div>

        <div className="prose prose-sm">
          <ReactMarkdown>{message.message}</ReactMarkdown>
        </div>

        {message.message_type === 'question' && (
          <Badge variant="outline" className="mt-2">
            Waiting for response
          </Badge>
        )}
      </div>
    </div>
  );
}
```

## Styling

### Tailwind Configuration

```js
export default {
  darkMode: ['class'],
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        // ... more colors
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
```

## Testing

### Vitest Setup

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardPage } from './DashboardPage';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

describe('DashboardPage', () => {
  it('renders metrics', async () => {
    const queryClient = createTestQueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <DashboardPage />
      </QueryClientProvider>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });
});
```

## Build & Deployment

### Production Build

```bash
npm run build
```

### Environment Variables

```env
VITE_API_URL=https://api.agentvine.example.com
VITE_WS_URL=wss://api.agentvine.example.com
```

### Docker

```dockerfile
FROM node:20-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Performance Optimization

- Code splitting with React.lazy()
- Memoization with useMemo/useCallback
- Virtual scrolling for long lists
- Image lazy loading
- Bundle size optimization
- Service worker for offline support
