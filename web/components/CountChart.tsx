"use client";

import { useEffect, useRef, useState } from "react";
import { Count } from "@/lib/api";

const H = 260;
const M = { top: 12, right: 96, bottom: 28, left: 40 };

const SERIES = [
  { key: "cumulative_unique", label: "Counted so far", color: "var(--series-1)" },
  { key: "visible", label: "In view", color: "var(--series-2)" },
] as const;

function niceMax(value: number) {
  const step = 10 ** Math.floor(Math.log10(Math.max(value, 1)));
  return Math.ceil(value / step) * step || 1;
}

/** Both lines share one scale (apples). The marker follows the video; click to seek. */
export function CountChart(props: {
  counts: Count[];
  fps: number;
  currentFrame: number;
  onSeek: (frame: number) => void;
}) {
  const { counts, fps, currentFrame, onSeek } = props;
  const ref = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState<number | null>(null);
  const [W, setW] = useState(800); // drawn at real width, so text stays readable on a phone
  useEffect(() => {
    if (!ref.current) return;
    setW(ref.current.clientWidth || 800);
    const observer = new ResizeObserver(([entry]) => setW(entry.contentRect.width || 800));
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [counts.length]);
  if (counts.length < 2) return null;

  // Even, so the middle gridline is a whole number of apples.
  const peak = niceMax(Math.max(...counts.map((c) => Math.max(c.cumulative_unique, c.visible))));
  const top = peak % 2 ? peak + 1 : peak;
  const lastFrame = counts[counts.length - 1].frame;
  const x = (frame: number) => M.left + (frame / lastFrame) * (W - M.left - M.right);
  const y = (value: number) => H - M.bottom - (value / top) * (H - M.top - M.bottom);
  // Counts are whole numbers, so the lines step instead of sloping between frames.
  const path = (key: "cumulative_unique" | "visible") =>
    counts.map((c, i) => {
      const px = x(c.frame).toFixed(1);
      return i ? `H${px}V${y(c[key]).toFixed(1)}` : `M${px} ${y(c[key]).toFixed(1)}`;
    }).join("");

  const frameAt = (clientX: number) => {
    const box = ref.current!.getBoundingClientRect();
    const svgX = ((clientX - box.left) / box.width) * W;
    const ratio = (svgX - M.left) / (W - M.left - M.right);
    return Math.max(0, Math.min(lastFrame, Math.round(ratio * lastFrame)));
  };

  const shown = counts.find((c) => c.frame === (hover ?? currentFrame)) ?? counts[0];
  const last = counts[counts.length - 1];
  const labelsY = [y(last.cumulative_unique), y(last.visible)];
  if (Math.abs(labelsY[0] - labelsY[1]) < 16) labelsY[1] = labelsY[0] + 16;
  const hoverLeft = hover === null ? 0 : (x(hover) / W) * 100;

  return (
    <div>
      <div className="legend">
        {SERIES.map((s) => (
          <span key={s.key}><i className="swatch" style={{ background: s.color }} />{s.label}</span>
        ))}
      </div>
      <div
        className="chart"
        ref={ref}
        onPointerMove={(e) => setHover(frameAt(e.clientX))}
        onPointerLeave={() => setHover(null)}
        onClick={(e) => onSeek(frameAt(e.clientX))}
      >
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Apples counted and in view over time">
          {[0, 0.5, 1].map((t) => (
            <g key={t}>
              <line x1={M.left} x2={W - M.right} y1={y(top * t)} y2={y(top * t)} stroke="var(--grid)" />
              <text x={M.left - 8} y={y(top * t) + 4} textAnchor="end">{Math.round(top * t)}</text>
            </g>
          ))}
          <text x={M.left} y={H - 8}>0s</text>
          <text x={W - M.right} y={H - 8} textAnchor="end">{(lastFrame / fps).toFixed(1)}s</text>
          {SERIES.map((s, i) => (
            <g key={s.key}>
              <path d={path(s.key)} fill="none" stroke={s.color} strokeWidth="2" strokeLinejoin="round" />
              <text className="label" x={W - M.right + 8} y={labelsY[i] + 4}>{last[s.key]} {i ? "in view" : "counted"}</text>
            </g>
          ))}
          <line x1={x(shown.frame)} x2={x(shown.frame)} y1={M.top} y2={H - M.bottom} stroke="var(--apple)" strokeWidth="2" />
          {SERIES.map((s) => (
            <circle key={s.key} cx={x(shown.frame)} cy={y(shown[s.key])} r="4" fill={s.color} stroke="var(--paper)" strokeWidth="2" />
          ))}
        </svg>
        {hover !== null && (
          <div
            className="chart-tooltip"
            style={hoverLeft > 60 ? { right: `${100 - hoverLeft + 2}%` } : { left: `${hoverLeft + 2}%` }}
          >
            {(shown.frame / fps).toFixed(1)}s, frame {shown.frame}<br />
            Counted so far: {shown.cumulative_unique}<br />
            In view: {shown.visible}
          </div>
        )}
      </div>
    </div>
  );
}
