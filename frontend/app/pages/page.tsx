// pages/chat.tsx
'use client'
import { useState } from 'react';
import ChatResponse from '../../components/ChatResponse';
import { parseResponse } from '../../utils/parseResponse';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState<any>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chatPsy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input })
      });
      const data = await res.json();
      setResponse(data);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Chat Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Assistant Psychiatrique</h1>
          <p className="mt-2 text-gray-600">Posez vos questions sur la dépression et la santé mentale</p>
        </div>

        {/* Chat Input */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="Décrivez vos symptômes..."
              required
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Envoi...' : 'Envoyer'}
            </button>
          </div>
        </form>

        {/* Response Display */}
        {response && (
          <ChatResponse 
            response={response.response} 
            sources={response.sources} 
          />
        )}
      </div>
    </div>
  );
}