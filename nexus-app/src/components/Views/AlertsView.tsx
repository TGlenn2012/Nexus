import React from 'react';

export const AlertsView: React.FC = () => {
  // Mock alerts for now - in a real app, this would come from a context or API
  const alerts = [
    { id: 1, type: 'info', message: 'System initialized successfully.', timestamp: new Date().toISOString() },
  ];

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>System Alerts</h2>
      </div>
      <div className="view-content">
        {alerts.length === 0 ? (
          <div className="empty-state">No active alerts.</div>
        ) : (
          <div className="alerts-list">
            {alerts.map(alert => (
              <div key={alert.id} className={`alert-item ${alert.type}`}>
                <div className="alert-timestamp">{new Date(alert.timestamp).toLocaleString()}</div>
                <div className="alert-message">{alert.message}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
