"use client";

import { useEffect, useState } from "react";

export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Run = {
  id: string;
  title: string;
  is_demo: boolean;
  model: string;
  trained_model: boolean;
  frames: number;
  fps_video: number;
  width: number;
  height: number;
  fps_processed: number;
  unique_apples: number;
  created_at: string;
};
export type Job = {
  id: string;
  video_id: string;
  status: "queued" | "running" | "done" | "failed";
  progress: number;
  error: string | null;
  run_id: string | null;
};
export type Count = { frame: number; visible: number; cumulative_unique: number };
export type Track = {
  track_id: number;
  first_frame: number;
  last_frame: number;
  length: number;
  mean_score: number;
};
export type Event = {
  frame: number;
  track_id: number;
  type: string;
  event_class: string;
  score: number;
};
export type Limits = {
  max_upload_mb: number;
  max_video_seconds: number;
  max_uploads_per_day: number;
  retention_days: number;
};
export type Metrics = { sMOTSA: number; MOTSA: number; MOTSP: number; [key: string]: number };
export type Benchmarks = {
  status: "pending" | "measured";
  split?: string;
  model?: string;
  hardware?: string;
  overall?: Metrics;
  sequences?: Record<string, Metrics>;
  HOTA?: number | null;
  baselines: { model: string; sMOTSA: number; MOTSA: number; MOTSP: number }[];
};

export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(API + path);
  if (!response.ok) throw new Error(await errorText(response));
  return response.json();
}

export async function errorText(response: Response): Promise<string> {
  let detail = `request failed (${response.status})`;
  try {
    const body = await response.json();
    if (typeof body.detail === "string") detail = body.detail;
  } catch {}
  // The API sends short phrases; the reader gets a sentence.
  return detail.charAt(0).toUpperCase() + detail.slice(1) + (/[.!?]$/.test(detail) ? "" : ".");
}

/** Fetch once on mount. data stays null until loaded; error is a sentence for the reader. */
export function useApi<T>(path: string): { data: T | null; error: string | null } {
  const [state, setState] = useState<{ data: T | null; error: string | null }>({
    data: null,
    error: null,
  });
  useEffect(() => {
    let live = true;
    getJson<T>(path)
      .then((data) => live && setState({ data, error: null }))
      .catch((e: Error) =>
        live &&
        setState({
          data: null,
          error: e.message === "Failed to fetch" ? "The API is not reachable right now." : e.message,
        }),
      );
    return () => {
      live = false;
    };
  }, [path]);
  return state;
}
