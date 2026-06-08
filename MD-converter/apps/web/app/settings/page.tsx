export default function SettingsPage() {
  return (
    <div className="page">
      <section className="page-heading">
        <h1>Settings</h1>
        <p>Operational defaults for retention, privacy, and converter behavior will live here.</p>
      </section>

      <section className="panel">
        <h2>Conversion defaults</h2>
        <div className="settings-list">
          <div className="setting-row">
            <span>Extract images</span>
            <span className="badge">enabled</span>
          </div>
          <div className="setting-row">
            <span>OCR</span>
            <span className="badge">auto</span>
          </div>
          <div className="setting-row">
            <span>Preferred converter</span>
            <span className="badge">auto</span>
          </div>
        </div>
      </section>
    </div>
  );
}

