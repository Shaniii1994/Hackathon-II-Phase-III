'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { isAuthenticated, getUserId } from '@/lib/auth';
import ChatWindow from '@/components/ChatKit/ChatWindow';
import TaskList from '@/components/TaskList';
import { Task } from '@/lib/api-client';
import apiClient from '@/lib/api-client';

export default function ChatPage() {
  const router = useRouter();
  const [isReady, setIsReady] = useState(false);
  const userId = getUserId();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    setIsReady(true);
  }, [router]);

  const {
    data: tasks = [],
    isLoading,
    error,
    refetch,
  } = useQuery<Task[]>({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await apiClient.get('/api/tasks');
      return response.data;
    },
    enabled: isReady,
  });

  if (!isReady) {
    return null;
  }

  return (
    <main className="min-h-screen py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AI Task Assistant</h1>
              <p className="mt-2 text-gray-600">
                Chat with the AI to manage your tasks using natural language
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/tasks')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors flex items-center"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                My Tasks
              </button>
              <button
                onClick={() => {
                  // Assuming logout function is available
                  localStorage.removeItem('access_token');
                  localStorage.removeItem('refresh_token');
                  localStorage.removeItem('user_id');
                  router.push('/login');
                }}
                className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors flex items-center"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Chat Window */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-1 border border-gray-200">
              <ChatWindow />
            </div>
          </div>

          {/* Task List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">
                  Your Tasks
                </h2>
                <span className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium">
                  {tasks.length} tasks
                </span>
              </div>

              {isLoading && (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>
              )}

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 mb-4">
                  Error loading tasks. Please try again.
                </div>
              )}

              {!isLoading && !error && tasks && (
                <TaskList tasks={tasks} onUpdate={refetch} />
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}