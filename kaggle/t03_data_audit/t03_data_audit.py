"""T03 data audit (Kaggle, CPU).

Downloads APPLE MOTS from Zenodo, verifies MD5, extracts it to /kaggle/working/APPLE_MOTS
(so later kernels can attach this kernel's output), and answers T03 unknowns U1-U5:
  U1 duplicate content between sequences (e.g. 6 vs 10)
  U2 ignore-region encoding in instance PNGs
  U3 sequences present / sequence 9
  U4 frame-name gaps (consecutive vs subsampled)
  U5 per-sequence frame and instance counts
Writes t03_report.json and evidence/ thumbnails.
"""
import hashlib, json, os, subprocess, sys, time, zipfile
from collections import Counter, defaultdict

import numpy as np
from PIL import Image

URL = "https://zenodo.org/records/5939726/files/APPLE_MOTS.zip?download=1"
MD5 = "1f9b8cd79f05469d656a01015889b55d"
SIZE = 5661248829
TMP = "/kaggle/tmp" if os.path.isdir("/kaggle/tmp") else "/tmp"
ZIP = os.path.join(TMP, "APPLE_MOTS.zip")
OUT = "/kaggle/working"
DATA = os.path.join(OUT, "APPLE_MOTS")
report = {"started": time.strftime("%Y-%m-%d %H:%M:%S")}


def log(*a):
    print(*a, flush=True)


def download():
    for attempt in range(5):
        r = subprocess.run(["curl", "-L", "--fail", "--retry", "5", "-C", "-", "-A",
                            "Mozilla/5.0", "-o", ZIP, URL])
        if r.returncode == 0 and os.path.getsize(ZIP) == SIZE:
            return
        log("download attempt", attempt, "rc", r.returncode,
            "size", os.path.getsize(ZIP) if os.path.exists(ZIP) else None)
        time.sleep(10)
    raise SystemExit("download failed")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


os.makedirs(TMP, exist_ok=True)
# Prefer an attached Kaggle dataset; Zenodo returns 403 to Kaggle workers.
attached = [os.path.join(r, f) for r, _, fs in os.walk("/kaggle/input") for f in fs
            if f == "APPLE_MOTS.zip"]
extracted = sorted(r for r, ds, _ in os.walk("/kaggle/input") if "instances" in ds)
if attached:
    ZIP = attached[0]
    report["zip_source"] = ZIP
elif extracted:
    ZIP = None
    report["zip_source"] = "already extracted by Kaggle: " + ", ".join(extracted)
else:
    report["zip_source"] = URL
    download()
if ZIP is None:
    DATA = "/kaggle/input"
    report["md5_ok"] = "not checkable (Kaggle extracted the zip); MD5 verified locally before upload"
else:
    report["zip_size"] = os.path.getsize(ZIP)
    report["zip_md5"] = md5(ZIP)
    report["md5_ok"] = report["zip_md5"] == MD5
    log("md5", report["zip_md5"], report["md5_ok"])
    if not report["md5_ok"]:
        raise SystemExit("MD5 mismatch")
    with zipfile.ZipFile(ZIP) as z:
        names = z.namelist()
        report["zip_entries"] = len(names)
        report["zip_top_level"] = sorted({n.split("/")[0] for n in names})
        z.extractall(DATA)
    if not ZIP.startswith("/kaggle/input"):
        os.remove(ZIP)

# ---- catalogue: every PNG grouped by (split_dir, kind, seq) ----
cat = defaultdict(list)  # (relative parent dir) -> [files]
for root, _, files in os.walk(DATA):
    pngs = sorted(f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg")))
    if pngs:
        cat[os.path.relpath(root, DATA)].extend(pngs)
other = []
for root, _, files in os.walk(DATA):
    for f in files:
        if not f.lower().endswith((".png", ".jpg", ".jpeg")):
            other.append(os.path.relpath(os.path.join(root, f), DATA))
report["non_image_files"] = other[:200]
report["image_dirs"] = {k: len(v) for k, v in sorted(cat.items())}
log(json.dumps(report["image_dirs"], indent=1))


def seq_of(d):
    return d.replace("\\", "/").split("/")[-1]


def kind_of(d):
    p = d.replace("\\", "/").lower()
    if "instance" in p or "mask" in p or "label" in p:
        return "instances"
    return "images"


dirs = {}
for d in cat:
    dirs.setdefault((kind_of(d), seq_of(d)), []).append(d)
report["dir_index"] = {f"{k}/{s}": v for (k, s), v in sorted(dirs.items())}

# ---- per-sequence statistics (U3, U4, U5, U2) ----
seq_stats = {}
for (kind, seq), ds in sorted(dirs.items()):
    if kind != "instances":
        continue
    d = ds[0]
    files = cat[d]
    ids_all = set()
    per_frame = []
    values = Counter()
    dtype = None
    for f in files:
        a = np.array(Image.open(os.path.join(DATA, d, f)))
        dtype = str(a.dtype)
        u, c = np.unique(a, return_counts=True)
        for val, cnt in zip(u.tolist(), c.tolist()):
            values[val] += cnt
        objs = [v for v in u.tolist() if v not in (0,) and v < 10000 and v // 1000 > 0]
        ids_all.update(objs)
        per_frame.append(len(objs))
    idx = []
    for f in files:
        stem = os.path.splitext(f)[0]
        idx.append(int(stem) if stem.isdigit() else None)
    gaps = Counter(b - a for a, b in zip(idx, idx[1:]) if a is not None and b is not None)
    classes = Counter(v // 1000 for v in values if v not in (0,))
    seq_stats[seq] = {
        "dir": d, "frames": len(files), "dtype": dtype,
        "first_frame": files[0], "last_frame": files[-1],
        "frame_index_gaps": dict(gaps.most_common(10)),
        "unique_instance_values": len(ids_all),
        "masks_total": int(sum(per_frame)),
        "masks_per_frame_mean": float(np.mean(per_frame)) if per_frame else 0,
        "class_ids_seen": dict(classes),
        "has_value_10000_ignore": 10000 in values,
        "ignore_pixels": int(values.get(10000, 0)),
        "example_values": sorted(values)[:15],
    }
    log(seq, seq_stats[seq]["frames"], seq_stats[seq]["unique_instance_values"],
        seq_stats[seq]["masks_total"], seq_stats[seq]["has_value_10000_ignore"])

# image sizes per sequence
for (kind, seq), ds in sorted(dirs.items()):
    if kind != "images":
        continue
    d = ds[0]
    sizes = Counter()
    for f in cat[d][:: max(1, len(cat[d]) // 10)]:
        sizes[Image.open(os.path.join(DATA, d, f)).size] += 1
    seq_stats.setdefault(seq, {})["image_dir"] = d
    seq_stats[seq]["image_frames"] = len(cat[d])
    seq_stats[seq]["image_sizes"] = {f"{w}x{h}": n for (w, h), n in sizes.items()}
report["sequences"] = seq_stats

# ---- U1: duplicate check between every pair of image sequences ----
img_dirs = {seq: ds[0] for (kind, seq), ds in dirs.items() if kind == "images"}


def thumb(path):
    return np.asarray(Image.open(path).convert("L").resize((64, 48)), dtype=np.float32)


thumbs = {}
for seq, d in img_dirs.items():
    fs = cat[d]
    pick = [fs[0], fs[len(fs) // 2], fs[-1]]
    thumbs[seq] = [thumb(os.path.join(DATA, d, f)) for f in pick]

pair_sim = {}
seqs = sorted(img_dirs)
for i, a in enumerate(seqs):
    for b in seqs[i + 1:]:
        diffs = [float(np.mean(np.abs(x - y))) for x, y in zip(thumbs[a], thumbs[b])]
        pair_sim[f"{a}-{b}"] = round(float(np.mean(diffs)), 2)
report["thumbnail_mean_abs_diff"] = dict(sorted(pair_sim.items(), key=lambda kv: kv[1])[:20])


def gray_overlay_mask(rgb, tolerance=3, min_area=400):
    """Same rule as avia.data.kitti_mots.gray_overlay_mask."""
    import cv2

    arr = rgb.astype(np.int16)
    flat = (np.abs(arr[..., 0] - arr[..., 1]) <= tolerance) & (
        np.abs(arr[..., 1] - arr[..., 2]) <= tolerance)
    _, labels, stats, _ = cv2.connectedComponentsWithStats(flat.astype(np.uint8), connectivity=4)
    keep = np.flatnonzero(stats[:, cv2.CC_STAT_AREA] >= min_area)
    keep = keep[keep != 0]
    return np.isin(labels, keep)


def overlay_truth(a, b, common):
    """Treat clean (a) vs overlaid (b) differences as the true overlay; score the detector."""
    import cv2

    rows = []
    for f in common[:: max(1, len(common) // 12)]:
        x = np.asarray(Image.open(os.path.join(DATA, img_dirs[a], f)).convert("RGB"), dtype=np.int16)
        y = np.asarray(Image.open(os.path.join(DATA, img_dirs[b], f)).convert("RGB"), dtype=np.uint8)
        if x.shape != y.shape:
            continue
        raw = (np.abs(x - y.astype(np.int16)).max(axis=2) > 8).astype(np.uint8)
        kernel = np.ones((9, 9), np.uint8)
        truth = cv2.morphologyEx(cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)),
                                 cv2.MORPH_CLOSE, kernel).astype(bool)
        found = gray_overlay_mask(y)
        inter, union = (truth & found).sum(), (truth | found).sum()
        row = {"frame": f, "truth_fraction": round(float(truth.mean()), 4),
               "detector_fraction": round(float(found.mean()), 4),
               "iou": round(float(inter / union), 4) if union else None,
               "max_abs_diff": int(np.abs(x - y.astype(np.int16)).max())}
        label = os.path.join(DATA, dirs[("instances", b)][0], f)
        if os.path.exists(label):
            ids = np.array(Image.open(label))
            objs = [v for v in np.unique(ids) if v not in (0, 10000)]
            row["gt_objects"] = len(objs)
            row["gt_objects_mostly_in_truth"] = int(sum(
                truth[ids == v].mean() > 0.5 for v in objs))
        rows.append(row)
        if len(rows) == 3:
            os.makedirs(os.path.join(OUT, "evidence"), exist_ok=True)
            Image.fromarray((truth * 255).astype(np.uint8)).resize((648, 486)).save(
                os.path.join(OUT, "evidence", f"overlay_truth_{b}.png"))
    return rows


dup = {}
for a, b in [("0006", "0010"), ("0007", "0011"), ("0008", "0012")]:
    if a not in img_dirs or b not in img_dirs:
        dup[f"{a}-{b}"] = "sequence missing"
        continue
    fa, fb = cat[img_dirs[a]], cat[img_dirs[b]]
    common = sorted(set(fa) & set(fb))
    eq_frac, gray_frac = [], []
    for f in common[:: max(1, len(common) // 25)]:
        x = np.asarray(Image.open(os.path.join(DATA, img_dirs[a], f)).convert("RGB"), dtype=np.int16)
        y = np.asarray(Image.open(os.path.join(DATA, img_dirs[b], f)).convert("RGB"), dtype=np.int16)
        if x.shape != y.shape:
            continue
        same = np.all(np.abs(x - y) <= 2, axis=2)
        eq_frac.append(float(same.mean()))
        diff_px = y[~same]
        if len(diff_px):
            spread = diff_px.max(axis=1) - diff_px.min(axis=1)
            gray_frac.append(float(np.mean(spread <= 6)))
    ia = os.path.join(DATA, dirs[("instances", a)][0]) if ("instances", a) in dirs else None
    ib = os.path.join(DATA, dirs[("instances", b)][0]) if ("instances", b) in dirs else None
    inst_same = None
    if ia and ib and common:
        f = common[len(common) // 2]
        if os.path.exists(os.path.join(ia, f)) and os.path.exists(os.path.join(ib, f)):
            ma = np.array(Image.open(os.path.join(ia, f)))
            mb = np.array(Image.open(os.path.join(ib, f)))
            inst_same = float(np.mean(ma == mb)) if ma.shape == mb.shape else "shape differs"
    dup[f"{a}-{b}"] = {
        "frames_a": len(fa), "frames_b": len(fb), "common_names": len(common),
        "names_only_in_a": sorted(set(fa) - set(fb))[:10],
        "names_only_in_b": sorted(set(fb) - set(fa))[:10],
        "overlay_truth_vs_detector": overlay_truth(a, b, common),
        "mean_identical_pixel_fraction": round(float(np.mean(eq_frac)), 4) if eq_frac else None,
        "diff_pixels_gray_fraction": round(float(np.mean(gray_frac)), 4) if gray_frac else None,
        "instance_png_identical_fraction_mid_frame": inst_same,
    }
report["duplicate_check"] = dup
log(json.dumps(dup, indent=1))

# sample images for evidence
ev = os.path.join(OUT, "evidence")
os.makedirs(ev, exist_ok=True)
for seq, d in sorted(img_dirs.items()):
    f = cat[d][len(cat[d]) // 2]
    Image.open(os.path.join(DATA, d, f)).convert("RGB").resize((648, 486)).save(
        os.path.join(ev, f"seq{seq}_mid.jpg"), quality=85)

report["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
json.dump(report, open(os.path.join(OUT, "t03_report.json"), "w"), indent=1)
log("DONE")
