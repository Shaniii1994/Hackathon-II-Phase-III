"use client"
import { ReactNode } from 'react';
import { isAuthenticated, getUserId } from '@/lib/auth';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { queryClient } from '@/lib/query-client';
import { QueryClientProvider } from '@tanstack/react-query';

function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </body>
    </html>
  );
}

export default function AppLayout({ children }: { children: ReactNode }) {
  if (!isAuthenticated()) {
    redirect('/login');
  }

  const userId = getUserId();

  const handleLogout = () => {
    // This will be handled client-side in the actual component
  };

  const handleNavigateToTasks = () => {
    // This will be handled client-side in the actual component
  };

  const handleNavigateToChat = () => {
    // This will be handled client-side in the actual component
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="bg-indigo-600 text-white p-2 rounded-lg font-bold text-xl">
                  ✓
                </div>
                <h1 className="ml-3 text-xl font-bold text-gray-900">TaskMaster Pro</h1>
              </div>
              <div className="hidden md:ml-6 md:flex md:space-x-8">
                <Link
                  href="/tasks"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  My Tasks
                </Link>
                <Link
                  href="/dashboard/chat"
                  className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                >
                  AI Assistant
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <div className="ml-3 relative">
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-700 hidden md:block">User ID: {userId}</span>
                  <Link
                    href="/logout"
                    className="flex items-center text-sm font-medium text-gray-700 hover:text-indigo-600"
                  >
                    <svg className="h-5 w-5 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Logout
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © {new Date().getFullYear()} TaskMaster Pro. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
