import React, { useState } from 'react';
import { CouncilResult } from '../../types';
import ReactMarkdown from 'react-markdown';

interface AgentDeliberationProps {
  results: CouncilResult[];
}

export const AgentDeliberation: React.FC<AgentDeliberationProps> = ({ results }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="agent-deliberation">
      <button 
        className="deliberation-toggle" 
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="toggle-icon">{isOpen ? '▼' : '▶'}</span>
        View Council Deliberation
      </button>

      {isOpen && (
        <div className="deliberation-content">
          {results.map((result, idx) => (
            <div key={idx} className="deliberation-card">
              <div className="card-header">
                <span className="role">{result.role.toUpperCase()} DELIBERATION:</span>
                <span className="model-info">Model: {result.model} | Latency: {Math.round(result.latency_ms)}ms</span>
              </div>
              <div className="card-body">
                <ReactMarkdown>{result.response}</ReactMarkdown>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
