"use client";

import { Benchmarks, useApi } from "@/lib/api";

export default function BenchmarksPage() {
  const { data, error } = useApi<Benchmarks>("/api/benchmarks");

  const head = (
    <section className="ground-label page-head">
      <div className="wrap">
        <h1>Benchmarks</h1>
        <p className="lede">
          Multi-object tracking and segmentation on the APPLE MOTS test sequences. Higher is better.
        </p>
      </div>
    </section>
  );
  if (error) return <>{head}<div className="wrap page-body"><p className="error">{error}</p></div></>;
  if (!data) return <>{head}<div className="wrap"><p className="loading">Loading…</p></div></>;

  const measured = data.status === "measured" && data.overall;
  const percent = (value: number) => (value * 100).toFixed(1);
  const bars = [
    ...(measured ? [{ model: "AVIA", value: data.overall!.sMOTSA * 100, own: true }] : []),
    ...data.baselines.map((b) => ({ model: b.model, value: b.sMOTSA, own: false })),
  ];
  const sequences = Object.entries(data.sequences ?? {});

  return (
    <>
      {head}
      <div className="wrap page-body">
        {!measured && (
          <p className="notice">
            AVIA&apos;s model has not been scored yet. This page fills in from the evaluation output
            and never shows an estimate.
          </p>
        )}

        <figure className="bars">
          {bars.map((bar) => (
            <div key={bar.model} className={bar.own ? "bar-row own" : "bar-row"}>
              <span>{bar.model}</span>
              <span className="bar-track">
                <span className="bar" style={{ width: `${bar.value * 1.4}%` }} />
                {bar.value.toFixed(1)}
              </span>
            </div>
          ))}
          <figcaption className="small muted">
            sMOTSA on the test sequences, as a percentage. AVIA is from this project&apos;s scorer;
            the others are published figures.
          </figcaption>
        </figure>

        <section className="section">
          <h2>All scores</h2>
          <div className="table-wrap">
            <table className="compact">
              <thead>
                <tr><th>Model</th><th className="num">sMOTSA</th><th className="num">MOTSA</th><th className="num">MOTSP</th></tr>
              </thead>
              <tbody>
                <tr className="own">
                  <td>AVIA</td>
                  <td className="num">{measured ? percent(data.overall!.sMOTSA) : "pending"}</td>
                  <td className="num">{measured ? percent(data.overall!.MOTSA) : "pending"}</td>
                  <td className="num">{measured ? percent(data.overall!.MOTSP) : "pending"}</td>
                </tr>
                {data.baselines.map((b) => (
                  // Baselines are published as percentages, AVIA's metrics as fractions.
                  <tr key={b.model}>
                    <td>{b.model}</td>
                    <td className="num">{b.sMOTSA.toFixed(1)}</td><td className="num">{b.MOTSA.toFixed(1)}</td><td className="num">{b.MOTSP.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="muted" style={{ marginTop: 12 }}>
            {measured && data.model ? `AVIA's row is the ${data.model} checkpoint. ` : ""}
            PointTrack and TrackR-CNN figures are as published in the APPLE MOTS paper (De Jong et
            al. 2022).
          </p>
        </section>

        {measured && sequences.length > 0 && (
          <section className="section">
            <h2>By sequence</h2>
            <div className="table-wrap">
              <table className="compact">
                <thead>
                  <tr>
                    <th>Sequence</th><th className="num">sMOTSA</th><th className="num">MOTSA</th>
                    <th className="num">MOTSP</th><th className="num">ID switches</th><th className="num wide-only">Frames</th>
                  </tr>
                </thead>
                <tbody>
                  {sequences.map(([name, s]) => (
                    <tr key={name}>
                      <td>{name}</td>
                      <td className="num">{percent(s.sMOTSA)}</td>
                      <td className="num">{percent(s.MOTSA)}</td>
                      <td className="num">{percent(s.MOTSP)}</td>
                      <td className="num">{s.IDS}</td>
                      <td className="num wide-only">{s.frames}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        <section className="section prose">
          <h2>How these were measured</h2>
          <p>
            AVIA&apos;s scores come from this project&apos;s own scorer, not the official evaluation
            tool, so treat the comparison with the published figures as close rather than exact.
          </p>
          {measured && data.hardware && data.overall!.fps !== undefined && (
            <p>Speed on a {data.hardware}: {data.overall!.fps.toFixed(1)} frames per second.</p>
          )}
          <p>Mask HOTA: {data.HOTA == null ? "pending" : data.HOTA.toFixed(1)}.</p>
        </section>
      </div>
    </>
  );
}
