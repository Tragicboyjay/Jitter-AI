const API_BASE_URL = 'http://127.0.0.1:8000';

export interface Message {
  content: string;
}

export interface MessageResponse {
  response: string;
}

export interface Being {
  name: string;
  bio: string;
  personality: string;
  modelProvider: string;
  contextId: string;
  system: string;
  knowledge: string[];
  exampleResponses: string[];
}

export async function sendMessage(content: string): Promise<MessageResponse> {
  const response = await fetch(`${API_BASE_URL}/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function getBeingDetails(): Promise<Being> {
  const response = await fetch(`${API_BASE_URL}/being`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}