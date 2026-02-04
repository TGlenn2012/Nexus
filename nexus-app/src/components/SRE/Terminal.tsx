import React, { useEffect, useRef } from 'react';

interface TerminalProps {
  logs: string[];
}

export const Terminal: React.FC<TerminalProps> = ({ logs }) => {
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="sre-terminal">
      <div className="terminal-header">
        SRE OBSERVABILITY TERMINAL
        <span className="terminal-controls">
           <span className="control-dot"></span>
        </span>
      </div>
      <div className="terminal-body" ref={terminalRef}>
        {logs.map((log, i) => (
          <div key={i} className="terminal-line">
            {log}
          </div>
        ))}
        <div className="terminal-cursor">_</div>
      </div>
    </div>
  );
};
