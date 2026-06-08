import { Download, RotateCcw, XCircle } from "lucide-react";
import { getConversionJob } from "../../../lib/api";

interface JobDetailPageProps {
  params: Promise<{ jobId: string }>;
}

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const { jobId } = await params;
  const job = await getConversionJob(jobId);

  return (
    <div className="page">
      <section className="page-heading">
        <h1>{job.file.filename}</h1>
        <p>Job {job.job_id}</p>
      </section>

      <section className="grid">
        <div className="panel">
          <h2>Progress</h2>
          <div className="progress" aria-label={`${job.progress.percent}% complete`}>
            <span style={{ width: `${job.progress.percent}%` }} />
          </div>
          <ul className="status-list">
            <li>
              <span>Status</span>
              <span className="badge">{job.status}</span>
            </li>
            <li>
              <span>Stage</span>
              <span>{job.progress.current_stage}</span>
            </li>
            <li>
              <span>Units</span>
              <span>
                {job.progress.completed_units} / {job.progress.total_units}
              </span>
            </li>
          </ul>
        </div>

        <aside className="panel">
          <h2>Actions</h2>
          <div className="button-row">
            <button className="button secondary" type="button">
              <RotateCcw aria-hidden size={18} />
              Retry
            </button>
            <button className="button danger" type="button">
              <XCircle aria-hidden size={18} />
              Cancel
            </button>
            <button className="button" disabled={job.status !== "succeeded"} type="button">
              <Download aria-hidden size={18} />
              Download
            </button>
          </div>
        </aside>
      </section>
    </div>
  );
}

