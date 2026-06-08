import type { ConversionJob } from "@md-converter/shared-types";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

interface HealthResponse {
  status: "ok" | "unavailable";
  app: string;
  version: string;
}

export async function getApiHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${apiBaseUrl}/health`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error("Health check failed");
    }

    return response.json() as Promise<HealthResponse>;
  } catch {
    return {
      status: "unavailable",
      app: "md-converter-api",
      version: "unknown"
    };
  }
}

export async function listConversionJobs(): Promise<ConversionJob[]> {
  try {
    const response = await fetch(`${apiBaseUrl}/api/conversions`, {
      cache: "no-store"
    });

    if (!response.ok) {
      return [];
    }

    return response.json() as Promise<ConversionJob[]>;
  } catch {
    return [];
  }
}

export async function getConversionJob(jobId: string): Promise<ConversionJob> {
  try {
    const response = await fetch(`${apiBaseUrl}/api/conversions/${jobId}`, {
      cache: "no-store"
    });

    if (response.ok) {
      return response.json() as Promise<ConversionJob>;
    }
  } catch {
    // Fall through to deterministic scaffold data for local UI work.
  }

  const now = new Date().toISOString();

  return {
    job_id: jobId,
    status: "queued",
    file: {
      filename: "example.pdf",
      content_type: "application/pdf",
      size_bytes: 157286400
    },
    progress: {
      total_units: 120,
      completed_units: 0,
      percent: 0,
      current_stage: "queued"
    },
    batches: {
      total: 0,
      queued: 0,
      running: 0,
      succeeded: 0,
      failed: 0
    },
    result: null,
    error: null,
    created_at: now,
    updated_at: now
  };
}

