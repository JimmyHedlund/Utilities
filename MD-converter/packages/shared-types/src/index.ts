export const jobStatuses = [
  "uploaded",
  "queued",
  "preflighting",
  "splitting",
  "running",
  "merging",
  "succeeded",
  "failed",
  "cancelling",
  "cancelled",
  "retrying"
] as const;

export type JobStatus = (typeof jobStatuses)[number];

export const batchStatuses = [
  "queued",
  "running",
  "succeeded",
  "failed",
  "cancelled",
  "skipped"
] as const;

export type BatchStatus = (typeof batchStatuses)[number];

export const uploadStages = [
  "uploading",
  "queued",
  "inspecting_file",
  "splitting",
  "converting",
  "merging",
  "complete",
  "failed"
] as const;

export type UploadStage = (typeof uploadStages)[number];

export const userFacingErrorCodes = [
  "unsupported_file_type",
  "file_too_large",
  "too_many_pages",
  "too_many_slides",
  "encrypted_pdf",
  "corrupt_file",
  "conversion_timeout",
  "conversion_failed",
  "partial_conversion"
] as const;

export type UserFacingErrorCode = (typeof userFacingErrorCodes)[number];

export interface FileSummary {
  filename: string;
  content_type: string;
  size_bytes: number;
}

export interface ProgressSummary {
  total_units: number;
  completed_units: number;
  percent: number;
  current_stage: string;
}

export interface BatchSummary {
  total: number;
  queued: number;
  running: number;
  succeeded: number;
  failed: number;
}

export interface ConversionJob {
  job_id: string;
  status: JobStatus;
  file: FileSummary;
  progress: ProgressSummary;
  batches: BatchSummary;
  result: ConversionResult | null;
  error: ConversionError | null;
  created_at: string;
  updated_at: string;
}

export interface ConversionResult {
  markdown_url: string | null;
  zip_url: string | null;
  expires_at: string | null;
}

export interface ConversionError {
  code: UserFacingErrorCode | "not_implemented";
  message: string;
}

export interface CreateUploadRequest {
  filename: string;
  content_type: string;
  size_bytes: number;
}

export interface CreateUploadResponse {
  file_id: string;
  upload_mode: "single" | "multipart";
  upload_urls: string[];
  storage_key: string;
}

export interface CreateConversionRequest {
  file_id: string;
  output_format: "markdown";
  options: {
    extract_images: boolean;
    ocr: "auto" | "enabled" | "disabled";
    preserve_page_breaks: boolean;
    preferred_converter: "auto" | "docling" | "pymupdf4llm" | "markitdown";
  };
}

export interface CreateConversionResponse {
  job_id: string;
  status: JobStatus;
}

