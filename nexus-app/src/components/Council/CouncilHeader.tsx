import React from 'react';
import { CouncilResult } from '../../types';

interface CouncilHeaderProps {
  status: 'idle' | 'processing' | 'complete';
  results?: CouncilResult[];
}

export const CouncilHeader: React.FC<CouncilHeaderProps> = ({ status, results }) => {
  const agents = [
    { id: 'phi3', name: 'Phi-3', role: 'LOGIC', color: 'cyan' },
    { id: 'gemma2', name: 'Gemma-2', role: 'CREATIVE', color: 'purple' },
    { id: 'qwen2', name: 'Qwen-2', role: 'SPEED', color: 'orange' }
  ];

  const getAgentStatus = (agentRole: string) => {
    if (status === 'idle') return 'standby';
    if (status === 'processing') return 'active';
    
    // Complete state - check results
    const result = results?.find(r => r.role.toLowerCase().includes(agentRole.toLowerCase()));
    if (!result) return 'standby'; // Default if not found
    return result.status === 'success' ? 'complete' : 'error';
  };

  return (
    <div className="council-header">
      <div className={`status-badge ${status}`}>
        <span className="status-label">STATUS:</span>
        <span className="status-value">
          {status === 'processing' ? 'ACTIVE INFERENCE: DIAGNOSING...' : 
           status === 'complete' ? 'COMPLETE | FINAL DIAGNOSIS DELIVERED' : 
           'SYSTEM READY'}
        </span>
      </div>

      <div className="agents-grid">
        {agents.map(agent => (
          <div key={agent.id} className={`agent-card ${getAgentStatus(agent.role)}`}>
            <div className="agent-role">{agent.role}</div>
            <div className="agent-name">{agent.name}</div>
            <div className="agent-status-indicator"></div>
          </div>
        ))}
      </div>
    </div>
  );
};
