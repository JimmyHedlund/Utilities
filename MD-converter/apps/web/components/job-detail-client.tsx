"use client";

import type { ConversionJob } from "@md-converter/shared-types";
import { Download, RefreshCw, RotateCcw, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { cancelConversion, getConversionDownload, getConversionJob, retryConversion } from "../lib/api";

interface JobDetailClientProps {
  initialJob: ConversionJob;
}

export function JobDetailClient({ initialJob }: JobDetailClientProps) {
  const [job, setJob] = useState(initialJob);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const canCancel = ["queued", "preflighting", "splitting", "running", "retrying"].includes(job.status);
  const canRetry = job.status === "failed";

  useEffect(() => {
    let isMounted = true;

    async function refresh() {
      const nextJob = await getConversionJob(initialJob.job_id);
      if (!isMounted) {
        return;
      }
      setJob(nextJob);

      if (nextJob.status === "succeeded") {
        setDownloadUrl(await getConversionDownload(nextJob.job_id));
      }
    }

    void refresh();
    const timer = window.setInterval(refresh, 2000);
    return () => {
      isMounted = false;
      window.clearInterval(timer);
    };
  }, [initialJob.job_id]);

  return (
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
          <li>
            <span>Batches</span>
            <span>
              {job.batches.succeeded}/{job.batches.total} succeeded, {job.batches.failed} failed
            </span>
          </li>
          {job.error ? (
            <li>
              <span>Error</span>
              <span>{job.error.message}</span>
            </li>
          ) : null}
        </ul>
      </div>

      <aside className="panel">
        <h2>Actions</h2>
        <div className="button-row">
          <button className="button secondary" onClick={() => void getConversionJob(job.job_id).then(setJob)} type="button">
            <RefreshCw aria-hidden size={18} />
            Refresh
          </button>
          <button
            className="button secondary"
            disabled={!canRetry}
            onClick={() => void retryConversion(job.job_id).then((nextJob) => nextJob && setJob(nextJob))}
            type="button"
          >
            <RotateCcw aria-hidden size={18} />
            Retry
          </button>
          <button
            className="button danger"
            disabled={!canCancel}
            onClick={() => void cancelConversion(job.job_id).then((nextJob) => nextJob && setJob(nextJob))}
            type="button"
          >
            <XCircle aria-hidden size={18} />
            Cancel
          </button>
          {downloadUrl ? (
            <a className="button" href={downloadUrl}>
              <Download aria-hidden size={18} />
              Download
            </a>
          ) : (
            <button className="button" disabled type="button">
              <Download aria-hidden size={18} />
              Download
            </button>
          )}
        </div>
      </aside>
    </section>
  );
}
