import React, { useState, useEffect } from 'react';
import { ChatInterface } from './components/ChatInterface';
import { DashboardLayout } from './components/Layout/DashboardLayout';
import { AlertsView } from './components/Views/AlertsView';
import { AgentsView } from './components/Views/AgentsView';
import { SettingsView } from './components/Views/SettingsView';
import './styles/theme.css';
import './styles/components.css';

type ViewType = 'dashboard' | 'alerts' | 'agents' | 'settings';

function App() {
  const [apiKey, setApiKey] = useState<string>('');
  const [isConfigured, setIsConfigured] = useState(false);
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');

  useEffect(() => {
    // Check for API key in environment variable or localStorage
    const envKey = import.meta.env.VITE_OPEN_WEBUI_API_KEY;
    const storedKey = localStorage.getItem('nexus_api_key');
    
    if (envKey && envKey !== 'your_api_key_here') {
      setApiKey(envKey);
      setIsConfigured(true);
    } else if (storedKey) {
      setApiKey(storedKey);
      setIsConfigured(true);
    }
  }, []);

  const handleApiKeySubmit = (key: string) => {
    if (key.trim()) {
      setApiKey(key.trim());
      localStorage.setItem('nexus_api_key', key.trim());
      setIsConfigured(true);
    }
  };

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <ChatInterface apiKey={apiKey} />;
      case 'alerts':
        return <AlertsView />;
      case 'agents':
        return <AgentsView />;
      case 'settings':
        return <SettingsView />;
      default:
        return <ChatInterface apiKey={apiKey} />;
    }
  };

  if (!isConfigured) {
    return (
      <div className="api-key-setup">
        <div className="api-key-card">
          <h1>Nexus MoA</h1>
          <p className="setup-subtitle">Configure API Key</p>
          <p className="setup-description">
            Enter your Open WebUI API key to connect to the Nexus pipeline.
            You can find this in Open WebUI Settings → Account.
          </p>
          <ApiKeyForm onSubmit={handleApiKeySubmit} />
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout currentView={currentView} onViewChange={setCurrentView}>
      {renderView()}
    </DashboardLayout>
  );
}

interface ApiKeyFormProps {
  onSubmit: (key: string) => void;
}

const ApiKeyForm: React.FC<ApiKeyFormProps> = ({ onSubmit }) => {
  const [key, setKey] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!key.trim()) {
      setError('Please enter an API key');
      return;
    }
    setError('');
    onSubmit(key);
  };

  return (
    <form onSubmit={handleSubmit} className="api-key-form">
      <input
        type="password"
        value={key}
        onChange={(e) => setKey(e.target.value)}
        placeholder="Enter your Open WebUI API key"
        className="api-key-input"
        autoFocus
      />
      {error && <p className="error-text">{error}</p>}
      <button type="submit" className="submit-button">
        Connect
      </button>
    </form>
  );
};

export default App;
