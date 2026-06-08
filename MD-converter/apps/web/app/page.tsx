import { FileUp, Play, ShieldCheck } from "lucide-react";
import { getApiHealth } from "../lib/api";

export default async function UploadPage() {
  const health = await getApiHealth();

  return (
    <div className="page">
      <section className="page-heading">
        <h1>Convert documents to Markdown</h1>
        <p>
          Upload a PDF or PowerPoint file, track batch conversion progress, and
          download Markdown with optional extracted assets.
        </p>
      </section>

      <section className="grid">
        <div className="panel">
          <div className="upload-zone">
            <FileUp aria-hidden size={48} />
            <div>
              <h2>Drop a PDF or PPTX</h2>
              <p className="muted">The upload workflow is scaffolded and ready for storage integration.</p>
            </div>
            <div className="button-row">
              <button className="button" type="button">
                <FileUp aria-hidden size={18} />
                Select file
              </button>
              <button className="button secondary" type="button">
                <Play aria-hidden size={18} />
                Create test job
              </button>
            </div>
          </div>
        </div>

        <aside className="panel">
          <h2>System status</h2>
          <ul className="status-list">
            <li>
              <span>API health</span>
              <span className="badge">{health.status}</span>
            </li>
            <li>
              <span>Upload validation</span>
              <span className="badge">stubbed</span>
            </li>
            <li>
              <span>Worker routing</span>
              <span className="badge">registered</span>
            </li>
          </ul>
          <p className="muted">
            <ShieldCheck aria-hidden size={16} /> Conversion will run outside the request path once queues are wired.
          </p>
        </aside>
      </section>
    </div>
  );
}

