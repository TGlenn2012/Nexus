import React from 'react';
import '../styles/components.css';

export const LoadingIndicator: React.FC = () => {
  return (
    <div className="loading-indicator">
      <div className="loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <p className="loading-text">Nexus is thinking...</p>
    </div>
  );
};
