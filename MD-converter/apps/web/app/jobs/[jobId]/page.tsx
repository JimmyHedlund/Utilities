import { JobDetailClient } from "../../../components/job-detail-client";
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

      <JobDetailClient initialJob={job} />
    </div>
  );
}
