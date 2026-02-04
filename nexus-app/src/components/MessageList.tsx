import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '../types';
import { ConfidenceMeter } from './Council/ConfidenceMeter';
import { AgentDeliberation } from './Council/AgentDeliberation';
import { Terminal } from './SRE/Terminal';

interface MessageListProps {
  messages: Message[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.role}`}>
          <div className="message-header">
             <span className="message-role">{message.role === 'user' ? 'User' : 'Judge'}</span>
             {message.timestamp && (
               <span className="message-time">
                 {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
               </span>
             )}
          </div>
          
          <div className="message-bubble">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          {/* Nexus Data Rendering */}
          {message.nexusData && (
            <div className="nexus-data-container">
               <div className="nexus-metrics-row">
                  <div className="metric-col">
                      <ConfidenceMeter score={message.nexusData.confidence} />
                  </div>
                  <div className="metric-col">
                      <AgentDeliberation results={message.nexusData.council_results} />
                  </div>
               </div>
               
               <Terminal logs={message.nexusData.sre_logs} />
            </div>
          )}
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};
