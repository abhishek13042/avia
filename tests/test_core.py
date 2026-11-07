import numpy as np
import pytest
from PIL import Image

from avia.data import kitti_mots, rle, splits
from avia.evaluation.mots import evaluate, kitti_mots_lines
from avia.events.engine import EventEngine
from avia.perception.color import ColorBlobDetector
from avia.pipeline import process_video
from avia.tracking.tracker import MaskTracker, iou_matrix
from avia.types import Detection, resolve_overlaps


def disc(x, y, r=8, size=(100, 120)):
    yy, xx = np.ogrid[: size[0], : size[1]]
    return (xx - x) ** 2 + (yy - y) ** 2 <= r ** 2


def test_rle_round_trip():
    rng = np.random.default_rng(1)
    for mask in (rng.random((40, 50)) > 0.7, np.ones((5, 5), bool), np.zeros((5, 5), bool)):
        encoded = rle.encode(mask)
        assert (rle.decode(encoded) == mask).all()
        text = rle.counts_to_string(encoded["counts"])
        assert rle.string_to_counts(text) == encoded["counts"]


def test_rle_matches_pycocotools():
    mask_utils = pytest.importorskip("pycocotools.mask")
    mask = np.random.default_rng(2).random((60, 40)) > 0.6
    expected = mask_utils.encode(np.asfortranarray(mask.astype(np.uint8)))["counts"].decode()
    assert rle.counts_to_string(rle.encode(mask)["counts"]) == expected


def test_instance_split_separates_ignore():
    ids = np.array([[0, 1001, 1001], [1002, 10000, 0]])
    masks, ignore = kitti_mots.split_instances(ids)
    assert sorted(masks) == [1001, 1002]
    assert ignore.sum() == 1 and masks[1001].sum() == 2


def test_overlay_found_by_diff_with_clean_copy(tmp_path):
    image = np.random.default_rng(3).integers(0, 255, (60, 60, 3), dtype=np.uint8)
    patched = image.copy()
    patched[10:40, 10:40] = 128
    for sequence, rgb in (("0006", image), ("0010", patched)):
        folder = tmp_path / "testing" / "images" / sequence
        folder.mkdir(parents=True)
        Image.fromarray(rgb).save(folder / "000000.png")
    (tmp_path / "testing" / "instances").mkdir()
    found = kitti_mots.overlay_mask(str(tmp_path), 10, 0)
    assert found[12:38, 12:38].all() and found.sum() < 1000
    assert kitti_mots.overlay_mask(str(tmp_path), 10, 1) is None
    assert kitti_mots.overlay_mask(str(tmp_path), 0, 0) is None


def test_splits_protect_test_data(tmp_path):
    assert len(splits.loso_folds()) == 6
    splits.assert_tuning_safe([0, 3])
    for bad in ([6], [11]):
        with pytest.raises(ValueError):
            splits.assert_tuning_safe(bad)
    log = str(tmp_path / "test_log.json")
    for _ in range(3):
        splits.record_test_evaluation(log, "run")
    with pytest.raises(RuntimeError):
        splits.record_test_evaluation(log, "one too many")


def test_overlaps_go_to_higher_score():
    a, b = disc(30, 30), disc(34, 30)
    out = resolve_overlaps([Detection(a, 0.5), Detection(b, 0.9)])
    assert out[0].score == 0.9 and not (out[0].mask & out[1].mask).any()


def test_iou_matrix():
    a = np.array([[1, 1, 0, 0]], dtype=np.float32)
    b = np.array([[1, 0, 1, 0], [1, 1, 0, 0]], dtype=np.float32)
    assert iou_matrix(a, b)[0].tolist() == pytest.approx([1 / 3, 1.0])


def test_tracker_keeps_ids_through_motion_and_gap():
    tracker = MaskTracker()
    image = np.zeros((100, 120, 3), np.uint8)
    seen = []
    for i in range(12):
        dets = [Detection(disc(20 + 2 * i, 30), 0.9), Detection(disc(90 - 2 * i, 70), 0.9)]
        if i == 6:
            dets = dets[:1]  # second apple is missed for one frame
        seen.append({o.track_id for o in tracker.update(image, dets)})
    assert seen[-1] == {1, 2}
    assert all(s <= {1, 2} for s in seen)


def test_tracker_recovers_low_score_detection():
    tracker = MaskTracker()
    image = np.zeros((100, 120, 3), np.uint8)
    for i in range(3):
        tracker.update(image, [Detection(disc(30, 30), 0.9)])
    out = tracker.update(image, [Detection(disc(30, 30), 0.2)])
    assert [o.track_id for o in out] == [1]


def test_tracker_ignores_weak_new_objects():
    tracker = MaskTracker()
    image = np.zeros((100, 120, 3), np.uint8)
    for _ in range(4):
        assert tracker.update(image, [Detection(disc(30, 30), 0.3)]) == []


def test_mots_metrics_known_values():
    m = disc(30, 30)
    gt = {0: {1: m}, 1: {1: m}, 2: {1: m}, 3: {1: m}}
    pred = {0: {7: m}, 1: {7: m}, 2: {8: m}, 3: {}}
    pred[1][9] = disc(80, 70)
    r = evaluate(gt, pred)
    assert (r["TP"], r["FP"], r["FN"], r["IDS"]) == (3, 1, 1, 1)
    assert r["MOTSA"] == pytest.approx(0.25) and r["sMOTSA"] == pytest.approx(0.25)
    assert r["MOTSP"] == pytest.approx(1.0)


def test_mots_false_positive_inside_ignore_region_is_not_counted():
    pred = {0: {1: disc(30, 30)}}
    assert evaluate({0: {}}, pred)["FP"] == 1
    assert evaluate({0: {}}, pred, ignore={0: np.ones((100, 120), bool)})["FP"] == 0


def test_kitti_line_format():
    line = kitti_mots_lines(4, {7: disc(30, 30)})[0].split(" ")
    assert line[:5] == ["4", "1007", "1", "100", "120"]


def test_events_lost_reappeared_and_count():
    engine = EventEngine()
    for f in range(5):
        engine.update(f, {1: (10.0, 10.0)})
    for f in range(5, 16):
        engine.update(f, {})
    engine.update(16, {1: (10.0, 10.0)})
    kinds = [e["type"] for e in engine.events]
    assert kinds == ["first_seen", "lost", "reappeared"]
    assert engine.counts[-1]["cumulative_unique"] == 1


def test_events_flags_possible_fragment_as_ranked_only():
    engine = EventEngine()
    for f in range(4):
        engine.update(f, {1: (10.0, 10.0)})
    engine.update(6, {2: (15.0, 10.0)})
    event = next(e for e in engine.events if e["type"] == "possible_fragment")
    assert event["event_class"] == "ranked_only" and event["details"]["previous_track"] == 1


def test_pipeline_end_to_end(video, tmp_path):
    out = tmp_path / "run"
    result = process_video(video, str(out), ColorBlobDetector())
    assert result["trained_model"] is False
    assert result["unique_apples"] == 3
    for name in ("annotated.webm", "masks.jsonl.gz", "tracks.json", "events.json", "counts.json"):
        assert (out / name).stat().st_size > 0


def test_pipeline_rejects_long_video(video, tmp_path):
    with pytest.raises(ValueError):
        process_video(video, str(tmp_path / "r"), ColorBlobDetector(), max_seconds=0.1)


def test_loader_reads_train_and_testing_folders(tmp_path):
    for part, sequence in (("train", "0000"), ("testing", "0010")):
        for kind in ("images", "instances"):
            folder = tmp_path / "APPLE_MOTS" / part / kind / sequence
            folder.mkdir(parents=True)
            (folder / "000000.png").write_bytes(b"")
    root = kitti_mots.find_root(str(tmp_path))
    assert kitti_mots.list_sequences(root) == [0, 10]
    assert "testing" in kitti_mots.list_frames(root, 10)[0].image_path
    assert "train" in kitti_mots.list_frames(root, 0)[0].image_path


def test_mots_scorer_handles_touching_and_empty_masks():
    a, b = np.zeros((20, 20), bool), np.zeros((20, 20), bool)
    a[2:10, 2:10] = True
    b[3:11, 3:11] = True
    empty = np.zeros((20, 20), bool)
    r = evaluate({0: {1: a, 2: empty}}, {0: {7: b, 8: empty}})
    inter, union = 49, 79
    assert (r["TP"], r["FN"], r["FP"]) == (1, 1, 1)
    assert r["MOTSP"] == pytest.approx(inter / union)
