import type {
  ConversionJob,
  CreateConversionResponse,
  CreateUploadResponse
} from "@md-converter/shared-types";

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

export async function createUploadSession(file: File): Promise<CreateUploadResponse> {
  const response = await fetch(`${apiBaseUrl}/api/uploads`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      filename: file.name,
      content_type: file.type,
      size_bytes: file.size
    })
  });

  if (!response.ok) {
    throw new Error("Could not create upload session");
  }

  return response.json() as Promise<CreateUploadResponse>;
}

export async function uploadFileToStorage(file: File, uploadUrl: string): Promise<void> {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    headers: {
      "Content-Type": file.type
    },
    body: file
  });

  if (!response.ok) {
    throw new Error("Could not upload file to storage");
  }
}

export async function completeUpload(fileId: string): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/uploads/${fileId}/complete`, {
    method: "POST"
  });

  if (!response.ok) {
    throw new Error("Could not complete upload");
  }
}

export async function createConversion(fileId: string): Promise<CreateConversionResponse> {
  const response = await fetch(`${apiBaseUrl}/api/conversions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      file_id: fileId,
      output_format: "markdown",
      options: {
        extract_images: true,
        ocr: "auto",
        preserve_page_breaks: true,
        preferred_converter: "auto"
      }
    })
  });

  if (!response.ok) {
    throw new Error("Could not create conversion");
  }

  return response.json() as Promise<CreateConversionResponse>;
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

export async function getConversionDownload(jobId: string): Promise<string | null> {
  const response = await fetch(`${apiBaseUrl}/api/conversions/${jobId}/download`, {
    cache: "no-store"
  });

  if (!response.ok) {
    return null;
  }

  const payload = (await response.json()) as { markdown_url: string };
  return payload.markdown_url;
}
