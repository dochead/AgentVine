// API Types
export type TaskType = 'feature' | 'bugfix' | 'test' | 'docs' | 'refactor' | 'review';
export type TaskStatus = 'queued' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
export type TaskPriority = 'low' | 'normal' | 'high' | 'critical';
export type WorkerStatus = 'idle' | 'busy' | 'waiting' | 'error' | 'offline';
export type SessionStatus = 'active' | 'idle' | 'terminated';

export interface Task {
  id: string;
  title: string;
  description: string;
  task_type: TaskType;
  status: TaskStatus;
  priority: TaskPriority;
  repository_url: string;
  branch_name: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface TaskCreate {
  title: string;
  description: string;
  task_type: TaskType;
  priority: TaskPriority;
  repository_url: string;
  branch_name: string;
}

export interface Worker {
  id: string;
  name: string;
  status: WorkerStatus;
  created_at: string;
  updated_at: string;
  last_heartbeat_at?: string;
}

export interface Session {
  id: string;
  session_id: string;
  worker_id: string;
  task_id?: string;
  status: SessionStatus;
  created_at: string;
  last_activity_at: string;
  terminated_at?: string;
}

export interface QueueStats {
  pending: number;
  started: number;
  finished: number;
  failed: number;
  deferred: number;
  scheduled: number;
}

export interface QueueStatsResponse {
  high_priority: QueueStats;
  default: QueueStats;
  low_priority: QueueStats;
  worker_requests: QueueStats;
  controller_responses: QueueStats;
}

export interface PendingMessage {
  message_id: string;
  session_id: string;
  task_id?: string;
  worker_id?: string;
  content: string;
  created_at: string;
}

export interface ConversationMessage {
  message_id: string;
  direction: 'worker_to_human' | 'human_to_worker';
  content: string;
  in_reply_to?: string;
  created_at: string;
}

export interface HumanResponse {
  message_id: string;
  response: string;
}
