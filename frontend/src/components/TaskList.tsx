'use client';

import { useState } from 'react';
import { z } from 'zod';
import apiClient, { Task } from '@/lib/api-client';

interface TaskListProps {
  tasks: Task[];
  onUpdate: () => void;
}

// Validation schema for editing
const editTaskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(100, 'Title must be less than 100 characters'),
  description: z.string().min(1, 'Description is required').max(500, 'Description must be less than 500 characters'),
  due_date: z.string().min(1, 'Due date is required'),
});

type EditTaskFormData = z.infer<typeof editTaskSchema>;

export default function TaskList({ tasks, onUpdate }: TaskListProps) {
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editFormData, setEditFormData] = useState({
    title: '',
    description: '',
    due_date: '',
  });
  const [editErrors, setEditErrors] = useState<Partial<Record<keyof EditTaskFormData, string>>>({});
  const [loadingTaskId, setLoadingTaskId] = useState<number | null>(null);
  const [error, setError] = useState('');

  const handleToggleComplete = async (taskId: number) => {
    setLoadingTaskId(taskId);
    setError('');

    try {
      await apiClient.patch(`/api/tasks/${taskId}/complete`);
      onUpdate();
    } catch (error: any) {
      setError('Failed to update task status');
    } finally {
      setLoadingTaskId(null);
    }
  };

  const handleStartEdit = (task: Task) => {
    setEditingTaskId(task.id);
    setEditFormData({
      title: task.title,
      description: task.description || '',
      due_date: task.due_date || '',
    });
    setEditErrors({});
    setError('');
  };

  const handleCancelEdit = () => {
    setEditingTaskId(null);
    setEditFormData({ title: '', description: '', due_date: '' });
    setEditErrors({});
  };

  const handleEditChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setEditFormData((prev) => ({ ...prev, [name]: value }));
    setEditErrors((prev) => ({ ...prev, [name]: '' }));
    setError('');
  };

  const handleSaveEdit = async (taskId: number) => {
    setEditErrors({});
    setError('');

    // Validate form
    const result = editTaskSchema.safeParse(editFormData);
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof EditTaskFormData, string>> = {};
      result.error.errors.forEach((error) => {
        const path = error.path[0] as keyof EditTaskFormData;
        fieldErrors[path] = error.message;
      });
      setEditErrors(fieldErrors);
      return;
    }

    setLoadingTaskId(taskId);

    try {
      await apiClient.put(`/api/tasks/${taskId}`, {
        title: editFormData.title,
        description: editFormData.description,
        due_date: editFormData.due_date,
      });
      setEditingTaskId(null);
      onUpdate();
    } catch (error: any) {
      setError('Failed to update task');
    } finally {
      setLoadingTaskId(null);
    }
  };

  const handleDelete = async (taskId: number) => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setLoadingTaskId(taskId);
    setError('');

    try {
      await apiClient.delete(`/api/tasks/${taskId}`);
      onUpdate();
    } catch (error: any) {
      setError('Failed to delete task');
    } finally {
      setLoadingTaskId(null);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const isOverdue = (dateString: string | null, completed: boolean) => {
    if (completed || !dateString) return false;
    const dueDate = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return dueDate < today;
  };

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">No tasks yet</h3>
        <p className="text-gray-500">Get started by creating your first task!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 gap-4">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`bg-white rounded-xl shadow-sm p-5 border-l-4 transition-all duration-200 hover:shadow-md ${
              task.is_complete
                ? 'border-green-500 bg-green-50/30'
                : isOverdue(task.due_date, task.is_complete)
                ? 'border-red-500 bg-red-50/30'
                : 'border-blue-500 bg-blue-50/30'
            }`}
          >
            {editingTaskId === task.id ? (
              // Edit Mode
              <div className="space-y-4">
                <div>
                  <input
                    type="text"
                    name="title"
                    value={editFormData.title}
                    onChange={handleEditChange}
                    className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                      editErrors.title ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Task title"
                  />
                  {editErrors.title && (
                    <p className="mt-1 text-xs text-red-600">{editErrors.title}</p>
                  )}
                </div>

                <div>
                  <textarea
                    name="description"
                    value={editFormData.description}
                    onChange={handleEditChange}
                    rows={2}
                    className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none ${
                      editErrors.description ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Task description"
                  />
                  {editErrors.description && (
                    <p className="mt-1 text-xs text-red-600">{editErrors.description}</p>
                  )}
                </div>

                <div>
                  <input
                    type="date"
                    name="due_date"
                    value={editFormData.due_date}
                    onChange={handleEditChange}
                    className={`w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                      editErrors.due_date ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {editErrors.due_date && (
                    <p className="mt-1 text-xs text-red-600">{editErrors.due_date}</p>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleSaveEdit(task.id)}
                    disabled={loadingTaskId === task.id}
                    className="flex-1 px-3 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center justify-center"
                  >
                    {loadingTaskId === task.id ? (
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    ) : null}
                    Save
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    disabled={loadingTaskId === task.id}
                    className="flex-1 px-3 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              // View Mode
              <>
                <div className="flex items-start justify-between mb-3">
                  <h3
                    className={`text-lg font-semibold ${
                      task.is_complete ? 'text-gray-500 line-through' : 'text-gray-900'
                    }`}
                  >
                    {task.title}
                  </h3>
                  <button
                    onClick={() => handleToggleComplete(task.id)}
                    disabled={loadingTaskId === task.id}
                    className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${
                      task.is_complete
                        ? 'bg-green-500 border-green-500'
                        : 'border-gray-300 hover:border-indigo-500'
                    }`}
                    title={task.is_complete ? 'Mark as incomplete' : 'Mark as complete'}
                  >
                    {task.is_complete && (
                      <svg
                        className="w-4 h-4 text-white"
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path d="M5 13l4 4L19 7"></path>
                      </svg>
                    )}
                  </button>
                </div>

                {task.description && (
                  <p
                    className={`text-sm mb-4 ${
                      task.is_complete ? 'text-gray-400' : 'text-gray-600'
                    }`}
                  >
                    {task.description}
                  </p>
                )}

                <div className="flex items-center justify-between text-sm mb-4">
                  <span
                    className={`font-medium ${
                      isOverdue(task.due_date, task.is_complete)
                        ? 'text-red-600'
                        : task.is_complete
                        ? 'text-gray-400'
                        : 'text-gray-700'
                    }`}
                  >
                    {task.due_date ? `Due: ${formatDate(task.due_date)}` : 'No due date'}
                  </span>
                  {task.is_complete && (
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                      Completed
                    </span>
                  )}
                  {isOverdue(task.due_date, task.is_complete) && !task.is_complete && (
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">
                      Overdue
                    </span>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleStartEdit(task)}
                    disabled={loadingTaskId === task.id}
                    className="flex-1 px-3 py-2 text-sm bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors flex items-center justify-center"
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(task.id)}
                    disabled={loadingTaskId === task.id}
                    className="flex-1 px-3 py-2 text-sm bg-red-50 text-red-600 rounded-lg hover:bg-red-100 disabled:opacity-50 transition-colors flex items-center justify-center"
                  >
                    {loadingTaskId === task.id ? (
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    ) : (
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    )}
                    {loadingTaskId === task.id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}