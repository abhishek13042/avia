"use client";

import Link from "next/link";
import { useApi } from "@/lib/api";
import { UntrainedNotice } from "@/components/UntrainedNotice";
import { UploadForm } from "@/components/UploadForm";

export default function UploadPage() {
  const { data: model } = useApi<{ trained: boolean }>("/api/models");

  return (
    <>
      <section className="ground-label page-head">
        <div className="wrap">
          <h1>Try a video</h1>
          <p className="lede">Upload a short orchard clip and get back a tracked video with a count.</p>
        </div>
      </section>
      <div className="wrap page-body">
        {model && !model.trained && <UntrainedNotice />}
        <div className="upload-grid">
          <div><UploadForm /></div>
          <div>
            <h2>You get back</h2>
            <ul className="returns">
              <li>The video with every tracked apple outlined</li>
              <li>A count of distinct apples, and how it grew over time</li>
              <li>Events where an apple was lost, came back, or may be a duplicate</li>
            </ul>
            <p className="small muted" style={{ marginTop: 14 }}>
              Works best on orchard rows filmed from a moving platform.{" "}
              <Link href="/about">Other footage may do worse.</Link>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
