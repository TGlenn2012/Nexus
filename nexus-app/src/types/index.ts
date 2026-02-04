export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
  nexusData?: NexusResponse; // Add optional nexusData to Message
}

export interface ChatCompletionRequest {
  model: string;
  messages: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
  }>;
}

export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface ApiError {
  error: {
    message: string;
    type?: string;
    code?: string;
  };
}

export interface CouncilResult {
  model: string;
  role: string;
  response: string;
  status: string;
  latency_ms: number;
  error?: string;
}

export interface NexusResponse {
  type: 'nexus_moa_response';
  content: string;
  confidence: number;
  council_results: CouncilResult[];
  sre_logs: string[];
}
