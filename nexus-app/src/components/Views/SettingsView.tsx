import React, { useState, useEffect } from 'react';

interface Settings {
  enabledAgents: {
    phi3: boolean;
    gemma2: boolean;
    qwen2: boolean;
  };
  maxTokens: number;
}

export const SettingsView: React.FC = () => {
  const [settings, setSettings] = useState<Settings>({
    enabledAgents: {
      phi3: true,
      gemma2: true,
      qwen2: true,
    },
    maxTokens: 1024,
  });

  useEffect(() => {
    const storedSettings = localStorage.getItem('nexus_settings');
    if (storedSettings) {
      setSettings(JSON.parse(storedSettings));
    }
  }, []);

  const saveSettings = (newSettings: Settings) => {
    setSettings(newSettings);
    localStorage.setItem('nexus_settings', JSON.stringify(newSettings));
  };

  const toggleAgent = (agent: keyof Settings['enabledAgents']) => {
    const newSettings = {
      ...settings,
      enabledAgents: {
        ...settings.enabledAgents,
        [agent]: !settings.enabledAgents[agent],
      },
    };
    saveSettings(newSettings);
  };

  const handleMaxTokensChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newSettings = {
      ...settings,
      maxTokens: parseInt(e.target.value, 10),
    };
    saveSettings(newSettings);
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h2>System Settings</h2>
      </div>
      <div className="view-content">
        <section className="settings-section">
          <h3>Active Council Members</h3>
          <div className="settings-group">
            <div className="setting-item">
              <label>
                <input 
                  type="checkbox" 
                  checked={settings.enabledAgents.phi3} 
                  onChange={() => toggleAgent('phi3')}
                />
                Phi-3 (Logic)
              </label>
            </div>
            <div className="setting-item">
              <label>
                <input 
                  type="checkbox" 
                  checked={settings.enabledAgents.gemma2} 
                  onChange={() => toggleAgent('gemma2')}
                />
                Gemma-2 (Creative)
              </label>
            </div>
            <div className="setting-item">
              <label>
                <input 
                  type="checkbox" 
                  checked={settings.enabledAgents.qwen2} 
                  onChange={() => toggleAgent('qwen2')}
                />
                Qwen-2 (Speed)
              </label>
            </div>
          </div>
        </section>

        <section className="settings-section">
          <h3>Response Configuration</h3>
          <div className="settings-group">
            <div className="setting-item">
              <label>Max Response Length (Tokens): {settings.maxTokens}</label>
              <input 
                type="range" 
                min="256" 
                max="4096" 
                step="256" 
                value={settings.maxTokens} 
                onChange={handleMaxTokensChange}
                className="range-slider"
              />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
