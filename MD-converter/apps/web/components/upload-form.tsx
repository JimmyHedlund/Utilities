"use client";

import { FileUp, Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import {
  completeUpload,
  createConversion,
  createUploadSession,
  uploadFileToStorage
} from "../lib/api";

const allowedTypes = new Set([
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation"
]);

export function UploadForm() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("Choose a PDF or PPTX file.");
  const [isBusy, setIsBusy] = useState(false);

  async function startConversion() {
    if (!file) {
      setStatus("Choose a file before starting.");
      return;
    }

    if (!allowedTypes.has(file.type)) {
      setStatus("Only PDF and PPTX files are supported in Phase 1.");
      return;
    }

    setIsBusy(true);
    try {
      setStatus("Creating upload session...");
      const upload = await createUploadSession(file);
      setStatus("Uploading file...");
      await uploadFileToStorage(file, upload.upload_urls[0]);
      setStatus("Verifying upload...");
      await completeUpload(upload.file_id);
      setStatus("Creating conversion job...");
      const job = await createConversion(upload.file_id);
      router.push(`/jobs/${job.job_id}`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Upload failed.");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <div className="upload-zone">
      <FileUp aria-hidden size={48} />
      <div>
        <h2>Drop a PDF or PPTX</h2>
        <p className="muted">{file ? `${file.name} (${Math.ceil(file.size / 1024)} KB)` : status}</p>
      </div>
      <input
        accept=".pdf,.pptx,application/pdf,application/vnd.openxmlformats-officedocument.presentationml.presentation"
        className="visually-hidden"
        onChange={(event) => {
          const selectedFile = event.target.files?.[0] ?? null;
          setFile(selectedFile);
          setStatus(selectedFile ? "Ready to upload." : "Choose a PDF or PPTX file.");
        }}
        ref={fileInputRef}
        type="file"
      />
      <div className="button-row">
        <button className="button" onClick={() => fileInputRef.current?.click()} type="button">
          <FileUp aria-hidden size={18} />
          Select file
        </button>
        <button className="button secondary" disabled={isBusy || !file} onClick={startConversion} type="button">
          <Play aria-hidden size={18} />
          Start conversion
        </button>
      </div>
      <p className="muted">{isBusy ? status : file ? status : "Phase 1 stores the file, queues a worker, and returns Markdown."}</p>
    </div>
  );
}

