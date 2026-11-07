"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { API, Job, Limits, errorText, useApi } from "@/lib/api";

type Stage =
  | { name: "idle" }
  | { name: "uploading"; fraction: number }
  | { name: "processing"; job: Job }
  | { name: "failed"; message: string; step: number | null };

const STEPS = ["Upload", "Queue", "Track"];

function stepOf(stage: Stage) {
  if (stage.name === "uploading") return 0;
  if (stage.name === "processing") return stage.job.status === "queued" ? 1 : 2;
  return null;
}

function detail(responseText: string) {
  try {
    const { detail } = JSON.parse(responseText);
    return typeof detail === "string" ? detail : null;
  } catch {
    return null;
  }
}

function send(file: File, onProgress: (fraction: number) => void): Promise<{ id: string }> {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    const form = new FormData();
    form.append("file", file);
    request.open("POST", `${API}/api/videos`);
    request.upload.onprogress = (e) => onProgress(e.loaded / e.total);
    request.onerror = () => reject(new Error("The upload failed. Check your connection."));
    request.onload = () => {
      if (request.status < 300) resolve(JSON.parse(request.responseText));
      else reject(new Error(detail(request.responseText) ?? "The upload failed."));
    };
    request.send(form);
  });
}

export function UploadForm() {
  const router = useRouter();
  const { data: limits } = useApi<Limits>("/api/limits");
  const [stage, setStage] = useState<Stage>({ name: "idle" });
  const [over, setOver] = useState(false);
  const [fileName, setFileName] = useState("");
  const stream = useRef<EventSource | null>(null);

  useEffect(() => () => stream.current?.close(), []);

  const fail = (message: string) =>
    setStage((last) => ({ name: "failed", message, step: stepOf(last) }));

  async function start(file: File) {
    try {
      setFileName(file.name);
      setStage({ name: "uploading", fraction: 0 });
      const video = await send(file, (fraction) => setStage({ name: "uploading", fraction }));
      const response = await fetch(`${API}/api/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id: video.id }),
      });
      if (!response.ok) throw new Error(await errorText(response));
      const job: Job = await response.json();
      setStage({ name: "processing", job });
      follow(job.id);
    } catch (e) {
      fail((e as Error).message);
    }
  }

  function follow(jobId: string) {
    const source = new EventSource(`${API}/api/jobs/${jobId}/events`);
    stream.current = source;
    source.onmessage = (message) => {
      const job: Job = JSON.parse(message.data);
      if (job.status === "done" && job.run_id) {
        source.close();
        router.push(`/runs/${job.run_id}`);
      } else if (job.status === "failed") {
        source.close();
        fail(job.error ?? "Processing failed.");
      } else {
        setStage({ name: "processing", job });
      }
    };
    source.onerror = () => {
      source.close();
      fail("Lost contact with the server. Check your connection and try again.");
    };
  }

  if (stage.name === "uploading" || stage.name === "processing") {
    const current = stage.name === "uploading" ? 0 : stage.job.status === "queued" ? 1 : 2;
    const fraction = stage.name === "uploading" ? stage.fraction : stage.job.progress;
    const words = ["Uploading…", "Waiting in the queue…", "Finding and tracking apples…"];
    return (
      <div className="working" aria-live="polite">
        <ol className="steps">
          {STEPS.map((step, i) => (
            <li
              key={step}
              aria-current={i === current ? "step" : undefined}
              data-state={i < current ? "done" : undefined}
            >
              {step}
            </li>
          ))}
        </ol>
        <p className="working-file">{fileName}</p>
        <div className="progress"><div style={{ width: `${fraction * 100}%` }} /></div>
        <p className="progress-line">
          <span>{words[current]}</span>
          <span>{Math.round(fraction * 100)}%</span>
        </p>
        <p className="small muted working-note">Keep this page open. This can take a while.</p>
      </div>
    );
  }

  return (
    <>
      {stage.name === "failed" && (
        <div className="failed">
          {stage.step !== null && (
            <ol className="steps">
              {STEPS.map((step, i) => (
                <li
                  key={step}
                  aria-current={i === stage.step ? "step" : undefined}
                  data-state={i < stage.step! ? "done" : i === stage.step ? "failed" : undefined}
                >
                  {step}
                </li>
              ))}
            </ol>
          )}
          {fileName && <p className="working-file">{fileName}</p>}
          <p className="error" role="alert">{stage.message}</p>
        </div>
      )}
      <label
        className={over ? "dropzone over" : "dropzone"}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setOver(false);
          if (e.dataTransfer.files[0]) start(e.dataTransfer.files[0]);
        }}
      >
        <input
          type="file"
          accept="video/*,.mkv"
          onChange={(e) => e.target.files?.[0] && start(e.target.files[0])}
        />
        <strong>{stage.name === "failed" ? "Choose another video" : "Choose a video"}</strong>
        <span>or drop it here</span>
      </label>
      {limits && (
        <p className="limits muted">
          MP4, MOV, WebM, MKV or AVI, up to {limits.max_upload_mb} MB and{" "}
          {limits.max_video_seconds} seconds. {limits.max_uploads_per_day} uploads a day. Your
          video and results are deleted after {limits.retention_days} days.
        </p>
      )}
    </>
  );
}
