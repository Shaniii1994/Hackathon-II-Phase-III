import React from 'react';
import { Task } from '@/lib/api-client';

interface TaskDisplayProps {
  tasks: Task[];
  onTaskUpdate?: () => void;
}

export default function TaskDisplay({ tasks, onTaskUpdate }: TaskDisplayProps) {
  if (tasks.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <p className="text-gray-500 text-center">No tasks to display</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-gray-800">Recent Tasks</h3>
      </div>
      <div className="divide-y">
        {tasks.slice(0, 5).map((task) => (
          <div key={task.id} className="p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between">
              <div>
                <h4 className={`font-medium ${task.is_complete ? 'line-through text-gray-500' : 'text-gray-800'}`}>
                  {task.title}
                </h4>
                {task.description && (
                  <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                )}
              </div>
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${
                  task.is_complete
                    ? 'bg-green-100 text-green-800'
                    : task.due_date && new Date(task.due_date) < new Date()
                    ? 'bg-red-100 text-red-800'
                    : 'bg-blue-100 text-blue-800'
                }`}
              >
                {task.is_complete ? 'Completed' : 'Pending'}
              </span>
            </div>
            {task.due_date && (
              <p className="text-xs text-gray-500 mt-2">
                Due: {new Date(task.due_date).toLocaleDateString()}
              </p>
            )}
          </div>
        ))}
      </div>
      {tasks.length > 5 && (
        <div className="p-4 text-center text-sm text-gray-500">
          And {tasks.length - 5} more tasks...
        </div>
      )}
    </div>
  );
}