# Kaggle runbook: from the zip to results

Account `abhishekg14`. CLI: `python -m kaggle`. Everything stays private and is named `avia-*`.

## 1. Check the download

The full file is 5,661,248,829 bytes with MD5 `1f9b8cd79f05469d656a01015889b55d`. Put it at `data/raw/APPLE_MOTS.zip`, replacing the partial file there.

```bash
md5sum data/raw/APPLE_MOTS.zip
```

Do not continue if the MD5 differs.

## 2. Create the private dataset

```bash
python -m kaggle datasets create -p data/raw
```

Wait until Kaggle shows the dataset as ready. Kaggle extracts the zip, so kernels see `/kaggle/input/apple-mots/APPLE_MOTS/{train,testing}`. If the upload fails with `Errno 2` on a `.kaggle/uploads` path, create that folder under the temp directory and retry.

## 3. Run the data audit (T03)

```bash
python -m kaggle kernels push -p kaggle/t03_data_audit
python -m kaggle kernels status abhishekg14/avia-t03-data-audit
python -m kaggle kernels output abhishekg14/avia-t03-data-audit -p artifacts/t03
```

Done on 2026-10-31; the results are in `artifacts/t03/t03_report.json` and the T03 task record. Run it again only if the dataset changes.

## 4. Train

`kaggle/t24_baseline/train_maskrcnn.py` resumes from `last.pt` and stops itself after 8.5 hours, so a long run can continue across sessions. `AVIA_FOLD` selects the held-out sequence. Unset, it trains the final model on sequences 0–5.

Kaggle does not take environment variables from the CLI. For each fold, set `FOLD` at the top of a copy of the script (line 25) and use a separate kernel id, such as `avia-t24-fold0`.

```bash
python -m kaggle kernels push -p kaggle/t24_baseline
python -m kaggle kernels status abhishekg14/avia-t24-baseline
python -m kaggle kernels output abhishekg14/avia-t24-baseline -p artifacts/t24
```

Use the six folds (0–5) to tune and report validation scores, then train the final model. To resume, attach the earlier kernel's output as a data source. The script looks for `last.pt` in its input as well as its output.

GPU training has only been tested as a CPU smoke run on synthetic data. Watch the first real epoch for memory and speed before leaving it to run.

## 5. Validate

Run this on Kaggle if the machine has no GPU. The build step packs the current code into one kernel script, which reads `model.pt` from the matching fold kernel.

```bash
python kaggle/t24_eval/build_kernel.py --fold 5 --out <folder>
python -m kaggle kernels push -p <folder>
python -m kaggle kernels output abhishekg14/avia-t24-fold5-eval -p artifacts/eval
```

With a local GPU and the zip extracted:

```bash
python scripts/evaluate.py --data data/APPLE_MOTS --detector maskrcnn:artifacts/t24/model.pt --sequences 5
```

Sequences 6–12 are refused here on purpose.

## 6. Test

The test set may be scored at most three times, and each use is logged in `artifacts/test_log.json`. Use it only on a locked configuration.

```bash
python scripts/evaluate.py --data data/APPLE_MOTS --detector maskrcnn:artifacts/t24/model.pt --test --note "locked baseline"
```

This writes `artifacts/benchmarks.json` and KITTI MOTS txt files.

## 7. Mask HOTA

`scripts/run_trackeval.py` needs [TrackEval](https://github.com/JonathonLuiten/TrackEval). It has **not been run yet**: only its ground-truth preparation is tested. TrackEval was not installed on the development machine, so check the first output against a hand-checked case.

```bash
python scripts/run_trackeval.py --data data/APPLE_MOTS --pred artifacts/eval/<model> --sequences 10 11 12 --summary artifacts/benchmarks.json
```

## 8. Publish

Follow the checklist in [MODEL_INTEGRATION.md](MODEL_INTEGRATION.md).
