import React from 'react';

export const AgentsView: React.FC = () => {
  const agents = [
    { 
      id: 'phi3', 
      name: 'Phi-3 (Logic Core)', 
      description: 'Specializes in analytical reasoning, structured logic, and step-by-step problem solving.',
      model: 'phi3',
      status: 'active'
    },
    { 
      id: 'gemma2', 
      name: 'Gemma-2 (Creative Core)', 
      description: 'Focuses on lateral thinking, generating diverse perspectives, and creative solutions.',
      model: 'gemma2:2b',
      status: 'active'
    },
    { 
      id: 'qwen2', 
      name: 'Qwen-2 (Speed Core)', 
      description: 'Optimized for rapid response generation and identifying key actionable insights.',
      model: 'qwen2:1.5b',
      status: 'active'
    },
    { 
      id: 'judge', 
      name: 'Llama-3 (Judge)', 
      description: 'Synthesizes inputs from the council to produce a final, high-confidence response.',
      model: 'llama3',
      status: 'active'
    }
  ];

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>Council Agents</h2>
      </div>
      <div className="view-content">
        <div className="agents-grid-large">
          {agents.map(agent => (
            <div key={agent.id} className="agent-card-large">
              <div className="agent-header">
                <h3>{agent.name}</h3>
                <span className={`status-badge ${agent.status}`}>{agent.status.toUpperCase()}</span>
              </div>
              <div className="agent-body">
                <p>{agent.description}</p>
                <div className="agent-meta">
                  <span className="label">Model:</span> {agent.model}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
