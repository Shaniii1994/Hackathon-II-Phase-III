import axios from 'axios';

interface Task {
  id: number;
  title: string;
  completed: boolean;
}

interface ChatMessage {
  message: string;
}

interface ChatResponse {
  success: boolean;
  response: string;
  user_id: number;
}

/**
 * Service for communicating with the AI agent backend
 */
export class AIAgentService {
  /**
   * Send a message to the AI agent and receive a response
   */
  static async sendMessage(userId: string, message: string): Promise<ChatResponse> {
    try {
      const response = await axios.post(`/api/${userId}/chat`, {
        message
      });
      
      return response.data;
    } catch (error) {
      console.error('Error sending message to AI agent:', error);
      throw error;
    }
  }

  /**
   * Process a natural language request to add a task
   */
  static async processAddTaskRequest(userId: string, message: string): Promise<{ success: boolean; taskId?: number; error?: string }> {
    try {
      const response = await this.sendMessage(userId, message);
      
      // In a real implementation, the AI agent would return structured data
      // For now, we'll just return a success indicator
      return {
        success: response.success,
        ...(response.success && { taskId: 1 }) // Placeholder task ID
      };
    } catch (error) {
      return {
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * Process a natural language request to list tasks
   */
  static async processListTasksRequest(userId: string, message: string): Promise<{ success: boolean; tasks?: Task[]; error?: string }> {
    try {
      const response = await this.sendMessage(userId, message);
      
      // In a real implementation, the AI agent would return structured task data
      // For now, we'll return a success indicator
      return {
        success: response.success,
        ...(response.success && { tasks: [] }) // Placeholder for tasks
      };
    } catch (error) {
      return {
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * Process a natural language request to complete a task
   */
  static async processCompleteTaskRequest(userId: string, message: string): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await this.sendMessage(userId, message);
      
      return {
        success: response.success
      };
    } catch (error) {
      return {
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * Process a natural language request to delete a task
   */
  static async processDeleteTaskRequest(userId: string, message: string): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await this.sendMessage(userId, message);
      
      return {
        success: response.success
      };
    } catch (error) {
      return {
        success: false,
        error: (error as Error).message
      };
    }
  }

  /**
   * Process a natural language request to update a task
   */
  static async processUpdateTaskRequest(userId: string, message: string): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await this.sendMessage(userId, message);
      
      return {
        success: response.success
      };
    } catch (error) {
      return {
        success: false,
        error: (error as Error).message
      };
    }
  }
}

export default AIAgentService;
