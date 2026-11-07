"use client";

import Link from "next/link";
import { use, useRef, useState } from "react";
import { API, Count, Event, Run, Track, useApi } from "@/lib/api";
import { countAt } from "@/lib/counts";
import { CountChart } from "@/components/CountChart";
import { Roller } from "@/components/Roller";
import { UntrainedNotice } from "@/components/UntrainedNotice";

const EVENT_NAMES: Record<string, string> = {
  first_seen: "First seen",
  lost: "Lost",
  reappeared: "Reappeared",
  possible_fragment: "Possible duplicate track",
  unusual_motion: "Unusual motion",
};
const FIRST_ROWS = 25;

export default function RunPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: run, error } = useApi<Run>(`/api/runs/${id}`);
  const { data: counts } = useApi<Count[]>(`/api/runs/${id}/counts`);
  const { data: events } = useApi<Event[]>(`/api/runs/${id}/events`);
  const { data: tracks } = useApi<Track[]>(`/api/runs/${id}/tracks`);
  const video = useRef<HTMLVideoElement>(null);
  const [frame, setFrame] = useState(0);
  const [started, setStarted] = useState(false);
  const [eventType, setEventType] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);

  if (error) return <div className="wrap page-body"><p className="error">{error}</p></div>;
  if (!run) return <div className="wrap"><p className="loading">Loading…</p></div>;

  const seek = (target: number) => {
    if (video.current) {
      video.current.currentTime = target / run.fps_video;
      video.current.scrollIntoView({ block: "nearest" });
    }
    setFrame(target);
    setStarted(true);
  };
  const notable = (events ?? []).filter((e) => e.type !== "first_seen");
  const eventTypes = [...new Set(notable.map((e) => e.type))];
  const matching = eventType ? notable.filter((e) => e.type === eventType) : notable;
  const shown = showAll ? matching : matching.slice(0, FIRST_ROWS);
  const filterEvents = (type: string | null) => {
    setEventType(type);
    setShowAll(false);
  };
  const now = counts ? countAt(counts, frame) : null;
  const atEnd = frame >= run.frames - 1;
  // Before the first play or seek, the box shows the finished count rather than 000.
  const counted = started && counts && !atEnd ? (now?.cumulative_unique ?? 0) : run.unique_apples;

  return (
    <>
      <section className="ground-label page-head">
        <div className="wrap"><h1>{run.title}</h1></div>
      </section>
      <div className="wrap page-body">
        {!run.trained_model && <UntrainedNotice />}
        <div className="run-grid">
          <video
            ref={video}
            className="player"
            src={`${API}/api/runs/${id}/video`}
            aria-label={`Tracked video: ${run.title}`}
            controls
            muted
            playsInline
            onPlay={() => setStarted(true)}
            onTimeUpdate={(e) => setFrame(Math.round(e.currentTarget.currentTime * run.fps_video))}
          />
          <aside className="count-box">
            <h2>Apples counted</h2>
            <Roller
              value={counted}
              places={String(run.unique_apples).length}
              label={`${counted} of ${run.unique_apples} apples counted at this point in the video`}
            />
            <p className="count-of muted">
              {started ? `of ${run.unique_apples} in this clip, ${now?.visible ?? 0} in view now` : "in this clip"}
            </p>
            <dl className="facts">
              <div><dt>Frames</dt><dd>{run.frames}</dd></div>
              {/* Examples were prepared offline, so their speed says nothing. Benchmarks has the measured one. */}
              {!run.is_demo && (
                <div><dt>Processing speed</dt><dd>{run.fps_processed.toFixed(run.fps_processed < 1 ? 2 : 1)} fps</dd></div>
              )}
              <div><dt>Model</dt><dd>{run.model}</dd></div>
            </dl>
            <p className="small muted" style={{ margin: "12px 0 0" }}>
              Counts tracks seen in at least three frames.{" "}
              {run.is_demo
                ? "This clip is a labelled test sequence, but this count was not compared with the labels. Tracking scores are on "
                : "This count has no ground truth behind it. Accuracy is measured separately, on "}
              <Link href="/benchmarks">the test sequences</Link>.
            </p>
          </aside>
        </div>

        <section className="section">
          <h2>Count over time</h2>
          {counts && (
            <>
              <CountChart counts={counts} fps={run.fps_video} currentFrame={frame} onSeek={seek} />
              <details>
                <summary>Show as a table</summary>
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Frame</th><th>Counted so far</th><th>In view</th></tr></thead>
                    <tbody>
                      {counts.filter((_, i) => i % Math.ceil(counts.length / 40) === 0).map((c) => (
                        <tr key={c.frame} className="seek" onClick={() => seek(c.frame)}>
                          <td><button type="button" className="seek-button">{c.frame}</button></td><td>{c.cumulative_unique}</td><td>{c.visible}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </details>
            </>
          )}
        </section>

        <section className="section">
          <h2>Events</h2>
          {events && notable.length === 0 && <p className="muted">Nothing unusual was flagged.</p>}
          {notable.length > 0 && (
            <>
              <p className="muted">
                Checkable events can be tested against labelled footage. Heuristic events are rules
                of thumb. Choose a time to jump the video there.
              </p>
              <div className="event-filters" role="group" aria-label="Filter events">
                <button type="button" aria-pressed={eventType === null} onClick={() => filterEvents(null)}>
                  All {notable.length}
                </button>
                {eventTypes.map((type) => (
                  <button key={type} type="button" aria-pressed={eventType === type} onClick={() => filterEvents(type)}>
                    {EVENT_NAMES[type] ?? type} {notable.filter((e) => e.type === type).length}
                  </button>
                ))}
              </div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Time</th><th>Event</th><th>Apple</th><th className="wide-only">Basis</th></tr></thead>
                  <tbody>
                    {shown.map((e, i) => (
                      <tr key={i} className="seek" aria-current={e.frame === frame ? "true" : undefined} onClick={() => seek(e.frame)}>
                        <td><button type="button" className="seek-button">{(e.frame / run.fps_video).toFixed(1)}s</button></td>
                        <td>
                          {EVENT_NAMES[e.type] ?? e.type}
                          <span className="event-basis muted">{e.event_class === "gt_derived" ? "Checkable" : "Heuristic"}</span>
                        </td>
                        <td>#{e.track_id}</td>
                        <td className="wide-only muted">{e.event_class === "gt_derived" ? "Checkable" : "Heuristic"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {shown.length < matching.length && (
                <button type="button" className="button quiet show-all" onClick={() => setShowAll(true)}>
                  Show all {matching.length}
                </button>
              )}
            </>
          )}

          {tracks && tracks.length > 0 && (
            <details>
              <summary>All tracks ({tracks.length}, of which {run.unique_apples} confirmed)</summary>
              <div className="table-wrap">
                <table className="compact">
                  <thead><tr><th>Apple</th><th className="num">First frame</th><th className="num">Last frame</th><th className="num">Length</th><th className="num">Mean score</th></tr></thead>
                  <tbody>
                    {tracks.map((t) => (
                      <tr key={t.track_id} className="seek" onClick={() => seek(t.first_frame)}>
                        <td><button type="button" className="seek-button">#{t.track_id}</button></td><td className="num">{t.first_frame}</td><td className="num">{t.last_frame}</td>
                        <td className="num">{t.length}</td><td className="num">{t.mean_score.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          )}
        </section>
      </div>
    </>
  );
}
