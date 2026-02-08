import React from 'react';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function Message({ role, content, timestamp }: MessageProps) {
  const isUser = role === 'user';
  
  // Format timestamp
  const formattedTime = new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className={`flex mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="mr-3 flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center">
            <span className="text-white text-xs font-bold">AI</span>
          </div>
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-indigo-600 text-white rounded-br-none'
            : 'bg-gray-100 text-gray-800 rounded-tl-none'
        }`}
      >
        <div className="whitespace-pre-wrap">{content}</div>
        <div
          className={`text-xs mt-1 text-right ${
            isUser ? 'text-indigo-200' : 'text-gray-500'
          }`}
        >
          {formattedTime}
        </div>
      </div>
      {isUser && (
        <div className="ml-3 flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
            <span className="text-gray-700 text-xs font-bold">U</span>
          </div>
        </div>
      )}
    </div>
  );
}