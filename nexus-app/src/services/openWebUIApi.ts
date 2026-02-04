import type { ChatCompletionRequest, ChatCompletionResponse, ApiError, Message } from '../types';

const API_URL = import.meta.env.VITE_OPEN_WEBUI_URL || 'http://localhost:3000';
const DEFAULT_MODEL = import.meta.env.VITE_NEXUS_MODEL || 'Nexus MoA';

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`); 
    return response.ok;
  } catch (error) {
    return false;
  }
}

export async function sendMessage(
  userMessage: string,
  apiKey: string,
  model: string = DEFAULT_MODEL,
  settings?: any,
  history: Message[] = []
): Promise<string> {
  const url = `${API_URL}/api/chat/completions`;

  // Map local Message history to API format, excluding any Nexus-specific metadata
  const apiMessages = [
    ...history.map((m) => ({
      role: m.role,
      content: m.content,
    })),
    {
      role: 'user' as const,
      content: userMessage,
    },
  ];

  const requestBody = {
    model,
    messages: apiMessages,
    stream: false,
    nexus_settings: settings // Pass settings to pipeline
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: { message: `HTTP ${response.status}: ${response.statusText}` },
      }));
      throw new Error(errorData.error?.message || `API request failed: ${response.statusText}`);
    }

    const data: ChatCompletionResponse = await response.json();
    
    if (data.choices && data.choices.length > 0) {
      return data.choices[0].message.content;
    }
    
    throw new Error('No response content in API response');
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error occurred while sending message');
  }
}
