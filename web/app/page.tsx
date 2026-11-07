"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { API, Benchmarks, Count, Run, useApi } from "@/lib/api";
import { countAt } from "@/lib/counts";
import { Roller } from "@/components/Roller";
import { UntrainedNotice } from "@/components/UntrainedNotice";
import { UploadForm } from "@/components/UploadForm";

function LiveScene({ run }: { run: Run }) {
  const { data: counts } = useApi<Count[]>(`/api/runs/${run.id}/counts`);
  const video = useRef<HTMLVideoElement>(null);
  const [frame, setFrame] = useState(0);
  const [still, setStill] = useState(false);
  const [playing, setPlaying] = useState(false);
  // Until the clip runs, the plate shows the finished count rather than a stuck 000.
  const count = playing && counts ? (countAt(counts, frame)?.cumulative_unique ?? 0) : run.unique_apples;
  const places = String(run.unique_apples).length;

  // Autoplay is a default, not a requirement: reduced motion or a refused play() hands the
  // player to the viewer.
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      video.current?.pause();
      setStill(true);
      return;
    }
    video.current?.play().catch(() => setStill(true));
  }, []);

  return (
    <figure className="hero-scene">
      <div className="scene-window">
        <video
          ref={video}
          src={`${API}/api/runs/${run.id}/video`}
          poster="/posters/orchard-row.jpg"
          aria-label={`Tracked orchard footage: ${run.title}`}
          autoPlay={!still}
          controls={still}
          muted
          loop
          playsInline
          onPlaying={() => setPlaying(true)}
          onTimeUpdate={(e) => setFrame(Math.round(e.currentTarget.currentTime * run.fps_video))}
        />
        <div className="count-plate">
          <span className="word">Apples<br />counted</span>
          <Roller value={count} places={places} label={`${run.unique_apples} apples counted in this clip`} />
        </div>
      </div>
      <figcaption className="scene-caption">
        {run.title}. {run.frames} frames, ending on {run.unique_apples} apples. The model misses
        some apples, and those are not counted. The grey patches are part of the dataset footage.{" "}
        <Link href={`/runs/${run.id}`}>Open this result</Link>
      </figcaption>
    </figure>
  );
}

function StillScene({ message }: { message: string }) {
  return (
    <figure className="hero-scene">
      <div className="scene-window">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/posters/orchard-row.jpg" alt="An apple tree row from the APPLE MOTS footage" />
      </div>
      <figcaption className="scene-caption">{message}</figcaption>
    </figure>
  );
}

/** Adds up what per-frame counting would report, from the same clip's own numbers. */
function WhyTracks({ run }: { run: Run }) {
  const { data: counts } = useApi<Count[]>(`/api/runs/${run.id}/counts`);
  const outlines = counts?.reduce((sum, c) => sum + c.visible, 0);

  return (
    <section className="band">
      <div className="wrap proof-grid">
        <div>
          <h2>Adding up frames overcounts</h2>
          <p>
            An apple that stays in shot is outlined in every frame it appears in. AVIA links those
            outlines into one track and counts the track once. A track can survive a short gap, but
            an apple hidden for longer can come back as a new track.
          </p>
        </div>
        {outlines !== undefined && (
          <dl className="tally">
            <div className="wrong"><dt>Apple outlines, all frames</dt><dd>{outlines.toLocaleString("en")}</dd></div>
            <div><dt>Distinct apples, same clip</dt><dd>{run.unique_apples.toLocaleString("en")}</dd></div>
          </dl>
        )}
      </div>
    </section>
  );
}

function Evidence() {
  const { data } = useApi<Benchmarks>("/api/benchmarks");
  if (!data) return null;
  const measured = data.status === "measured" && data.overall;

  return (
    <section className="band">
      <div className="wrap evidence-grid">
        <div>
          <h2>Scored on footage it never trained on</h2>
          <p>
            Tracking and segmentation on the APPLE MOTS test sequences, measured with this
            project&apos;s own scorer. Higher is better. PointTrack and TrackR-CNN are the figures
            published with the dataset.
          </p>
          <p><Link href="/benchmarks">How these were measured</Link></p>
        </div>
        <div className="table-wrap">
          <table className="compact">
            <thead>
              <tr><th>Model</th><th className="num">sMOTSA</th><th className="num">MOTSA</th><th className="num">MOTSP</th></tr>
            </thead>
            <tbody>
              <tr className="own">
                <td>AVIA</td>
                <td className="num">{measured ? (data.overall!.sMOTSA * 100).toFixed(1) : "pending"}</td>
                <td className="num">{measured ? (data.overall!.MOTSA * 100).toFixed(1) : "pending"}</td>
                <td className="num">{measured ? (data.overall!.MOTSP * 100).toFixed(1) : "pending"}</td>
              </tr>
              {data.baselines.map((b) => (
                <tr key={b.model}>
                  <td>{b.model}</td>
                  <td className="num">{b.sMOTSA.toFixed(1)}</td><td className="num">{b.MOTSA.toFixed(1)}</td><td className="num">{b.MOTSP.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const { data: runs, error } = useApi<Run[]>("/api/gallery");
  const anyUntrained = runs?.some((run) => !run.trained_model);
  // Newest first from the API. The oldest demo leads: the poster is that clip's first frame.
  const lead = runs?.findLast((run) => run.trained_model) ?? runs?.[0];

  return (
    <>
      <section className="ground-label hero">
        <div className="wrap hero-grid">
          <h1>Count every apple in an orchard video</h1>
          <p className="lede">
            AVIA outlines the apples it can see in each frame, links them into tracks, and counts
            tracks rather than frames.
          </p>
          {lead ? (
            <LiveScene run={lead} />
          ) : (
            <StillScene
              message={
                error ??
                (runs ? "No examples have been published yet." : "Loading a finished example…")
              }
            />
          )}
          <div className="hero-action"><UploadForm /></div>
        </div>
      </section>

      {lead && <WhyTracks run={lead} />}

      <section className="band">
        <div className="wrap">
          <h2>Finished examples</h2>
          {anyUntrained && <UntrainedNotice />}
          {error && <p className="error">{error}</p>}
          {runs?.length === 0 && <p className="muted">No examples have been published yet.</p>}
          <div className="boxes">
            {runs?.map((run) => (
              <Link key={run.id} className="box" href={`/runs/${run.id}`}>
                <span className="box-picture">
                  <video src={`${API}/api/runs/${run.id}/video#t=1`} aria-label={`Tracked video: ${run.title}`} muted preload="metadata" />
                  <span className="box-count">{run.unique_apples}</span>
                </span>
                <strong>{run.title}</strong>
                <span className="muted">{run.unique_apples} apples, {run.frames} frames</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <Evidence />

      <section className="ground-label band">
        <div className="wrap close-grid">
          <h2>Bring your own row</h2>
          <div className="actions">
            <Link className="button" href="/upload">Try your own video</Link>
            <Link className="button quiet" href="/about">Read the limits</Link>
          </div>
        </div>
      </section>
    </>
  );
}
