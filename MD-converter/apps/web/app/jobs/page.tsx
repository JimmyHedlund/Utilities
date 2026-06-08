import Link from "next/link";
import { listConversionJobs } from "../../lib/api";

export default async function JobsPage() {
  const jobs = await listConversionJobs();

  return (
    <div className="page">
      <section className="page-heading">
        <h1>Jobs</h1>
        <p>Conversion history and progress will appear here once persistence is connected.</p>
      </section>

      <section className="panel">
        <h2>Recent conversions</h2>
        {jobs.length === 0 ? (
          <p className="muted">No conversion jobs yet.</p>
        ) : (
          <div className="status-list">
            {jobs.map((job) => (
              <Link className="job-row" href={`/jobs/${job.job_id}`} key={job.job_id}>
                <span>{job.file.filename}</span>
                <span className="badge">{job.status}</span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

