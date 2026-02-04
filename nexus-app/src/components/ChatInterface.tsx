import React, { useState, useEffect } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { LoadingIndicator } from './LoadingIndicator';
import { CouncilHeader } from './Council/CouncilHeader';
import { sendMessage } from '../services/openWebUIApi';
import type { Message, NexusResponse, CouncilResult } from '../types';
import '../styles/components.css';

interface ChatInterfaceProps {
  apiKey: string;
}

interface ChatSession {
  id: string;
  title: string;
  createdAt: string;
  messages: Message[];
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ apiKey }) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>([]);
  
  // Nexus specific state
  const [nexusStatus, setNexusStatus] = useState<'idle' | 'processing' | 'complete'>('idle');
  const [latestCouncilResults, setLatestCouncilResults] = useState<CouncilResult[] | undefined>(undefined);

  const activeSession = sessions.find((s) => s.id === activeSessionId) || null;

  const createNewSession = (): ChatSession => ({
    id: `session-${Date.now()}`,
    title: 'New Chat',
    createdAt: new Date().toISOString(),
    messages: [],
  });

  // Chat sessions persistence
  useEffect(() => {
    const storedSessions = localStorage.getItem('nexus_sessions');
    const storedActiveId = localStorage.getItem('nexus_active_session');

    if (storedSessions) {
      try {
        const parsed: ChatSession[] = JSON.parse(storedSessions);
        if (parsed.length > 0) {
          setSessions(parsed);
          const initialId = storedActiveId && parsed.some((s) => s.id === storedActiveId)
            ? storedActiveId
            : parsed[0].id;
          setActiveSessionId(initialId);
          return;
        }
      } catch {
        // ignore parse errors and fall through to create a fresh session
      }
    }

    const initial = createNewSession();
    setSessions([initial]);
    setActiveSessionId(initial.id);
  }, []);

  useEffect(() => {
    localStorage.setItem('nexus_sessions', JSON.stringify(sessions));
    if (activeSessionId) {
      localStorage.setItem('nexus_active_session', activeSessionId);
    }
  }, [sessions, activeSessionId]);

  const handleNewSession = () => {
    const next = createNewSession();
    setSessions((prev) => [...prev, next]);
    setActiveSessionId(next.id);
    setSuggestedPrompts([]);
    setError(null);
    setNexusStatus('idle');
    setLatestCouncilResults(undefined);
  };

  const handleDeleteSession = () => {
    if (!activeSession) return;
    if (!window.confirm('Delete this chat? This cannot be undone.')) return;

    setSessions((prev) => {
      const filtered = prev.filter((s) => s.id !== activeSession.id);
      if (filtered.length === 0) {
        const fresh = createNewSession();
        setActiveSessionId(fresh.id);
        return [fresh];
      }
      const nextActive = filtered[filtered.length - 1];
      setActiveSessionId(nextActive.id);
      return filtered;
    });
  };

  const handleSend = async (content: string) => {
    if (!activeSession) {
      return;
    }

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeSession.id
          ? { ...s, messages: [...s.messages, userMessage] }
          : s
      )
    );
    setIsLoading(true);
    setNexusStatus('processing');
    setError(null);

    // Read settings from localStorage
    const storedSettings = localStorage.getItem('nexus_settings');
    const settings = storedSettings ? JSON.parse(storedSettings) : undefined;

    try {
      const history = [...activeSession.messages, userMessage];
      const rawResponse = await sendMessage(content, apiKey, undefined, settings, history);
      let assistantMessageFull: Message;
      let councilResults: CouncilResult[] | undefined;

      try {
        // Try to parse Nexus JSON response
        const nexusData: NexusResponse = JSON.parse(rawResponse);
        if (nexusData.type === 'nexus_moa_response') {
           assistantMessageFull = {
             role: 'assistant',
             content: nexusData.content,
             timestamp: new Date(),
             nexusData: nexusData
           };
           councilResults = nexusData.council_results;
        } else {
           // If it's JSON but not our type (unlikely from our pipeline but possible from errors)
           throw new Error('Not a Nexus response');
        }
      } catch (e) {
        // Fallback to plain text if JSON parse fails or type mismatch
        assistantMessageFull = {
          role: 'assistant',
          content: rawResponse,
          timestamp: new Date(),
        };
      }

      // Typewriter-style streaming of the assistant response
      const streamingMessage: Message = { ...assistantMessageFull, content: '' };
      setSessions((prev) =>
        prev.map((s) =>
          s.id === activeSession.id
            ? { ...s, messages: [...s.messages, streamingMessage] }
            : s
        )
      );

      const fullText = assistantMessageFull.content;
      const chunkSize = 4;
      let index = 0;

      const interval = setInterval(() => {
        index += chunkSize;
        const nextContent = fullText.slice(0, index);
        setSessions((prev) =>
          prev.map((s) => {
            if (s.id !== activeSession.id) return s;
            if (s.messages.length === 0) return s;
            const updatedMessages = [...s.messages];
            const lastIndex = updatedMessages.length - 1;
            updatedMessages[lastIndex] = {
              ...updatedMessages[lastIndex],
              content: nextContent,
            };
            return { ...s, messages: updatedMessages };
          })
        );

        if (index >= fullText.length) {
          clearInterval(interval);
        }
      }, 25);

      setNexusStatus('complete');
      if (councilResults) setLatestCouncilResults(councilResults);

      // Simple follow-up suggestions based on last user message
      const trimmed = content.trim();
      const topicSnippet = trimmed.length > 60 ? `${trimmed.slice(0, 57)}...` : trimmed;
      setSuggestedPrompts([
        `Tell me more details about: "${topicSnippet || 'that'}"`,
        `Give me practical examples related to "${topicSnippet || 'this topic'}".`,
        `Summarize the most important takeaways from your last answer.`,
      ]);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      setNexusStatus('idle');
      
      const errorResponse: Message = {
        role: 'assistant',
        content: `⚠️ Error: ${errorMessage}`,
        timestamp: new Date(),
      };
      if (activeSession) {
        setSessions((prev) =>
          prev.map((s) =>
            s.id === activeSession.id
              ? { ...s, messages: [...s.messages, errorResponse] }
              : s
          )
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = () => {
    if (!activeSession) return;

    const exportText = activeSession.messages.map(m => 
      `### ${m.role.toUpperCase()} (${m.timestamp?.toLocaleString()})\n\n${m.content}\n`
    ).join('\n---\n\n');
    
    const blob = new Blob([exportText], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nexus-export-${new Date().toISOString()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="chat-interface">
      <div className="chat-interface-header">
         <CouncilHeader status={nexusStatus} results={latestCouncilResults} />
         {activeSession && activeSession.messages.length > 0 && (
            <button className="export-button" onClick={handleExport} title="Export to Markdown">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
              </svg>
            </button>
         )}
      </div>
      
      {/* Session management bar */}
      <div className="session-bar">
        <div className="session-tabs">
          {sessions.map((session) => (
            <button
              key={session.id}
              className={`session-tab ${session.id === activeSessionId ? 'active' : ''}`}
              type="button"
              onClick={() => setActiveSessionId(session.id)}
            >
              {session.title || 'Untitled'}
            </button>
          ))}
        </div>
        <div className="session-actions">
          <button
            type="button"
            className="session-icon-button"
            title="New Chat"
            onClick={handleNewSession}
          >
            +
          </button>
          {activeSession && (
            <>
              <button
                type="button"
                className="session-icon-button"
                title="Download Chat"
                onClick={handleExport}
              >
                ⬇
              </button>
              <button
                type="button"
                className="session-icon-button"
                title="Delete Chat"
                onClick={handleDeleteSession}
              >
                🗑
              </button>
            </>
          )}
        </div>
      </div>

      <div className="chat-content">
        <MessageList messages={activeSession?.messages ?? []} />
        
        {isLoading && <LoadingIndicator />}
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>

      {/* Suggested follow-up prompts */}
      {suggestedPrompts.length > 0 && (
        <div className="followup-container">
          {suggestedPrompts.map((prompt, idx) => (
            <button
              key={idx}
              className="followup-chip"
              type="button"
              onClick={() => handleSend(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      <div className="chat-footer">
        <MessageInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
};
