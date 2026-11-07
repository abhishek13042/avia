# Product

<!-- impeccable:product-schema 1 -->

> Inferred from the repository and the owner's stated goal, without an interview. Items marked
> (assumed) are the owner's to correct.

## Platform

web

## Users

- Reviewers of a computer vision resume: hiring managers and engineers with a few minutes, often
  on a phone, deciding whether the work is real. (assumed primary audience, from the owner's goal
  of making this their top resume project)
- Curious members of the public and growers who try the tool on their own short orchard clip.
  (assumed)

## Product Purpose

AVIA segments, tracks and counts apples in orchard video. A visitor watches a finished example or
uploads a clip, then gets back a tracked video, a count, and the events behind that count. Success
is a visitor seeing a real result within seconds and being able to check how it was measured.

## Positioning

AVIA counts tracks, not detections, so an apple that leaves hide and reveal is counted once. It
publishes its own measured scores beside the published baselines, on sequences kept out of training.

## Operating Context

- Upload flow is asynchronous: upload, queue, worker, result page, with live progress.
- Examples in the public gallery are precomputed, so a first visit needs no GPU wait.
- Public limits apply: file size, clip length, uploads per day, and retention all come from the API.

## Capabilities and Constraints

- Pages: home and gallery, upload, run result, benchmarks, about.
- A run shows the tracked video, unique apple count, count over time, events, and tracks.
- Events are either checkable against ground truth or heuristic, and the UI says which.
- Next.js frontend talking to a FastAPI backend. Backend, data and deployment are out of design scope.
- Mask HOTA is pending until TrackEval is run, and the UI shows it as pending.
- Undecided: public URL, hosting, sign-in.

## Brand Commitments

- The name is AVIA. No logo exists.
- Plain, exact voice. Terms visitors see: apples counted, in view, tracks, events.

## Evidence on Hand

- Test result, APPLE MOTS sequences 10 to 12, project scorer: sMOTSA 43.0, MOTSA 55.8, MOTSP 81.2,
  1.8 FPS on a Tesla T4 (`artifacts/benchmarks.json`).
- Published baselines from the dataset paper: PointTrack 38.7, 52.9, 80.0; TrackR-CNN 35.7, 47.8,
  80.4.
- Leave-one-sequence-out validation, sMOTSA 42.3 (`artifacts/eval/loso_summary.json`).
- Real footage: APPLE MOTS, De Jong et al. 2022, CC BY 4.0, credit required.
- None exist, and none may be invented: testimonials, customers, users, deployments, field trials.

## Product Principles

1. Show the result before explaining it.
2. Every number names how it was measured.
3. State limits where the result appears, not in a footnote.
4. Never present an estimate as a measurement. Unmeasured means "pending".

## Accessibility & Inclusion

No product-specific standard is set. Work to WCAG 2.2 AA, with charts readable as tables and
identity never carried by colour alone. (assumed)
