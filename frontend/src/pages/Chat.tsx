import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getPendingMessages, getConversation, sendHumanResponse } from '../api';
import type { PendingMessage } from '../types';

export default function Chat() {
  const queryClient = useQueryClient();
  const [selectedMessage, setSelectedMessage] = useState<PendingMessage | null>(null);
  const [response, setResponse] = useState('');

  // Fetch pending messages
  const { data: pendingMessages = [] } = useQuery({
    queryKey: ['pendingMessages'],
    queryFn: getPendingMessages,
  });

  // Fetch conversation for selected message
  const { data: conversation = [] } = useQuery({
    queryKey: ['conversation', selectedMessage?.session_id],
    queryFn: () => getConversation(selectedMessage!.session_id),
    enabled: !!selectedMessage?.session_id,
  });

  // Send response mutation
  const responseMutation = useMutation({
    mutationFn: sendHumanResponse,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingMessages'] });
      queryClient.invalidateQueries({ queryKey: ['conversation'] });
      setResponse('');
      setSelectedMessage(null);
    },
  });

  const handleSendResponse = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMessage || !response.trim()) return;

    responseMutation.mutate({
      message_id: selectedMessage.message_id,
      response: response.trim(),
    });
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Worker Chat</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Messages List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">
            Pending Messages ({pendingMessages.length})
          </h2>

          {pendingMessages.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No pending messages</p>
          ) : (
            <div className="space-y-3">
              {pendingMessages.map((msg) => (
                <div
                  key={msg.message_id}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedMessage?.message_id === msg.message_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedMessage(msg)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex gap-2">
                      {msg.task_id && (
                        <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                          Task: {msg.task_id.slice(0, 8)}...
                        </span>
                      )}
                      {msg.worker_id && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          Worker: {msg.worker_id.slice(0, 8)}...
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-gray-500">
                      {formatTimestamp(msg.created_at)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 line-clamp-2">{msg.content}</p>
                  {msg.session_id && (
                    <p className="text-xs text-gray-400 mt-1">
                      Session: {msg.session_id}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Conversation View & Response */}
        <div className="bg-white rounded-lg shadow-md p-6 flex flex-col">
          {selectedMessage ? (
            <>
              <h2 className="text-xl font-semibold mb-4">Conversation</h2>

              {/* Conversation History */}
              <div className="flex-1 overflow-y-auto mb-4 space-y-3 max-h-96 border border-gray-200 rounded-lg p-4">
                {conversation.length === 0 ? (
                  <p className="text-gray-500 text-center">No messages in conversation</p>
                ) : (
                  conversation.map((msg) => (
                    <div
                      key={msg.message_id}
                      className={`p-3 rounded-lg ${
                        msg.direction === 'worker_to_human'
                          ? 'bg-blue-50 border-l-4 border-blue-500'
                          : 'bg-green-50 border-l-4 border-green-500'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-1">
                        <span className="text-xs font-semibold">
                          {msg.direction === 'worker_to_human' ? '🤖 Worker' : '👤 Human'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(msg.created_at)}
                        </span>
                      </div>
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  ))
                )}
              </div>

              {/* Response Form */}
              <form onSubmit={handleSendResponse} className="mt-auto">
                <div className="mb-3">
                  <label className="block text-sm font-medium mb-2">
                    Your Response
                  </label>
                  <textarea
                    value={response}
                    onChange={(e) => setResponse(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    placeholder="Type your response to the worker..."
                    required
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={!response.trim() || responseMutation.isPending}
                    className="flex-1 bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    {responseMutation.isPending ? 'Sending...' : 'Send Response'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedMessage(null);
                      setResponse('');
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              Select a message to view conversation and respond
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
