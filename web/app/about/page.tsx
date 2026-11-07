export default function AboutPage() {
  return (
    <>
      <section className="ground-label page-head">
        <div className="wrap">
          <h1>About AVIA</h1>
          <p className="lede">
            Counting fruit from video is hard because the same apple appears in many frames and
            leaves keep hiding it. Counting per frame overcounts; AVIA counts tracks.
          </p>
        </div>
      </section>
      <div className="wrap page-body">
        <div className="prose">
          <h2>How it works</h2>
          <p>
            Each frame goes through an instance segmentation network that outlines the apples it
            finds. A tracker links those outlines across frames and can bridge a short gap, so an
            apple hidden briefly can keep its identity. The count is the number of confirmed tracks,
            meaning tracks seen in at least three frames. An event layer then flags apples that were
            lost, reappeared, or look like a duplicate track.
          </p>
          <h2>Data</h2>
          <p>
            The model is trained on APPLE MOTS, published by De Jong et al. in 2022 under CC BY 4.0.
            Test sequences are kept out of training and tuning, and scored only a few times.
          </p>
          <h2>Limits</h2>
          <p>
            Results depend on how close a clip is to the training data: orchard rows filmed from a
            moving platform. Other crops, lighting and camera angles may do worse. The model misses
            some apples even on that footage, and a long gap can split one apple into two tracks.
            Events marked heuristic are rules of thumb that have no ground truth to check against.
          </p>
        </div>
      </div>
    </>
  );
}
