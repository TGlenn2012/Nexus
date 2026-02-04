import React, { useState } from 'react';

interface ConfidenceMeterProps {
  score: number; // 0-100
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({ score }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const getColor = (val: number) => {
    if (val >= 80) return 'var(--color-success)'; // Green
    if (val >= 50) return 'var(--color-warning)'; // Amber
    return 'var(--color-error)'; // Red
  };

  const color = getColor(score);
  
  return (
    <div className="confidence-meter-container">
      <div className="confidence-header">
        <span className="confidence-label">Confidence Score: {Math.round(score)}%</span>
        <div 
          className="info-icon"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
          </svg>
          
          {showTooltip && (
            <div className="tooltip">
              <p>The Confidence Score (0-100%) represents the aggregate certainty of the Nexus Council.</p>
              <p>It is calculated based on:</p>
              <ul>
                <li>Agreement between active agents</li>
                <li>Individual model certainty (when available)</li>
                <li>Judge's evaluation of the synthesis</li>
              </ul>
            </div>
          )}
        </div>
      </div>
      <div className="confidence-track">
        <div 
          className="confidence-bar" 
          style={{ 
            width: `${score}%`,
            backgroundColor: color,
            boxShadow: `0 0 10px ${color}`
          }}
        ></div>
      </div>
    </div>
  );
};
