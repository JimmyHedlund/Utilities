import { ShieldCheck } from "lucide-react";
import { UploadForm } from "../components/upload-form";
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
          <UploadForm />
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
              <span className="badge">enabled</span>
            </li>
            <li>
              <span>Worker routing</span>
              <span className="badge">queued</span>
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
