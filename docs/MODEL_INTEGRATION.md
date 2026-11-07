# Model integration

The application depends on one interface, in `src/avia/perception/base.py`:

```python
class Detector(Protocol):
    name: str        # shown on every result
    trained: bool    # False shows the "placeholder model" notice
    def detect(self, image_bgr: np.ndarray) -> list[Detection]: ...
```

`Detection` holds a boolean H x W `mask` and a `score`.

## Choosing the model

Set `DETECTOR_SPEC` on both the API and the worker.

| Value | Model |
|---|---|
| `color` | Untrained colour placeholder (default) |
| `maskrcnn:artifacts/model.pt` | Checkpoint from `kaggle/t24_baseline` |
| `package.module:factory` | Any other model; `factory()` returns a Detector |

The worker loads the model when it starts. Restart it after changing the value. Results already stored keep the model name they were made with.

## Adding a new architecture

1. Write a class with `name`, `trained = True` and `detect()`.
2. Add a factory function that loads its weights.
3. Install the module where the worker runs, and set `DETECTOR_SPEC=your.module:factory`.

No API, database or frontend change is needed.

## After plugging in a model

1. Run `scripts/evaluate.py` on validation sequences to confirm it scores sensibly.
2. Spend a test evaluation only on a locked configuration (see [KAGGLE_RUNBOOK.md](KAGGLE_RUNBOOK.md)).
3. Copy `artifacts/benchmarks.json` to where `BENCHMARKS_PATH` points. The benchmarks page reads it at once.
4. Publish real examples: `python scripts/seed_demo.py --frames data/APPLE_MOTS/testing/images/0010 --title "Sequence 10"`.
5. Remove the synthetic gallery entry by starting from a fresh database, or delete its row.
6. Fill in [MODEL_CARD.md](MODEL_CARD.md) and the results table in the README.
