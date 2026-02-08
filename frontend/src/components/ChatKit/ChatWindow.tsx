'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { getUserId } from '@/lib/auth';
import apiClient from '@/lib/api-client';
import Message from './Message';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function ChatWindow() {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const userId = getUserId();

  // Mutation for sending messages
  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      if (!userId) {
        throw new Error('User not authenticated');
      }
      
      const response = await apiClient.post(`/api/${userId}/chat`, {
        message: message,
      });
      return response.data;
    },
    onSuccess: (data) => {
      // Add the AI response as a new message
      if (data && data.response) {
        const aiMessage: Message = {
          id: `ai-${Date.now()}`,
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      }
      setInputValue('');
    },
  });

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !sendMessageMutation.isPending) {
      // Add user message optimistically
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: inputValue,
        timestamp: new Date().toISOString(),
      };

      // Add user message to the state immediately
      setMessages(prev => [...prev, userMessage]);
      
      sendMessageMutation.mutate(inputValue);
    }
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-5">
        <div className="flex items-center">
          <div className="bg-white/20 p-2 rounded-lg">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <div className="ml-4">
            <h2 className="text-xl font-bold">AI Task Assistant</h2>
            <p className="text-indigo-200 text-sm">Powered by advanced AI technology</p>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-gray-50 to-gray-100">
        <>
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="mx-auto bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-1">How can I help you today?</h3>
              <p className="text-gray-500 max-w-md mx-auto">
                Ask me to manage your tasks using natural language. Try: "Add a task to buy groceries"
              </p>
              <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
                <button 
                  onClick={() => setInputValue("Add a task to buy groceries")}
                  className="text-left px-4 py-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Add a task to buy groceries
                </button>
                <button 
                  onClick={() => setInputValue("Show me my tasks")}
                  className="text-left px-4 py-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Show me my tasks
                </button>
                <button 
                  onClick={() => setInputValue("Mark task 1 as complete")}
                  className="text-left px-4 py-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Mark task 1 as complete
                </button>
                <button 
                  onClick={() => setInputValue("Update task 2 to add a due date")}
                  className="text-left px-4 py-3 bg-white rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Update task 2 to add a due date
                </button>
              </div>
            </div>
          )}
          {messages.map((message) => (
            <Message
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
            />
          ))}
          {sendMessageMutation.isPending && (
            <div className="flex items-start mb-4">
              <div className="mr-3 flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center">
                  <span className="text-white text-xs font-bold">AI</span>
                </div>
              </div>
              <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%]">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me to manage your tasks (e.g., 'Add a task to buy groceries')..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            disabled={sendMessageMutation.isPending}
          />
          <button
            type="submit"
            disabled={sendMessageMutation.isPending || !inputValue.trim()}
            className="px-5 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
        </form>
        {sendMessageMutation.error && (
          <p className="mt-2 text-red-600 text-sm text-center">
            {(sendMessageMutation.error as Error).message}
          </p>
        )}
      </div>
    </div>
  );
}