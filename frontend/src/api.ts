import axios from 'axios';
import type {
  Task,
  TaskCreate,
  Worker,
  Session,
  QueueStatsResponse,
  PendingMessage,
  ConversationMessage,
  HumanResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tasks API
export const getTasks = async (): Promise<Task[]> => {
  const { data } = await api.get<Task[]>('/api/v1/tasks');
  return data;
};

export const getTask = async (id: string): Promise<Task> => {
  const { data } = await api.get<Task>(`/api/v1/tasks/${id}`);
  return data;
};

export const createTask = async (task: TaskCreate): Promise<Task> => {
  const { data } = await api.post<Task>('/api/v1/tasks', task);
  return data;
};

// Workers API
export const getWorkers = async (): Promise<Worker[]> => {
  const { data } = await api.get<Worker[]>('/api/v1/workers');
  return data;
};

// Sessions API
export const getSessions = async (): Promise<Session[]> => {
  const { data } = await api.get<Session[]>('/api/v1/sessions');
  return data;
};

// Queue API
export const getQueueStats = async (): Promise<QueueStatsResponse> => {
  const { data } = await api.get<QueueStatsResponse>('/api/v1/queue/status');
  return data;
};

// Chat API
export const getPendingMessages = async (): Promise<PendingMessage[]> => {
  const { data } = await api.get<PendingMessage[]>('/api/v1/chat/pending');
  return data;
};

export const getConversation = async (sessionId: string): Promise<ConversationMessage[]> => {
  const { data } = await api.get<ConversationMessage[]>(`/api/v1/chat/conversation/${sessionId}`);
  return data;
};

export const sendHumanResponse = async (response: HumanResponse): Promise<any> => {
  const { data } = await api.post('/api/v1/chat/human-response', response);
  return data;
};

export default api;
