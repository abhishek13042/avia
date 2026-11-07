"""T24 baseline: Mask R-CNN R50-FPN on APPLE MOTS (Kaggle GPU, standalone, resumable).

Set FOLD to a sequence 0-5 for a LOSO run, or None to train the final model on all of 0-5.
Writes to /kaggle/working: last.pt (resume state), model.pt (loadable by the app, see
docs/MODEL_INTEGRATION.md) and metrics.json. To resume after the time limit, add this kernel's
output as an input and rerun; last.pt is found anywhere under /kaggle/input.

The AVIA_* environment variables exist only for the local smoke test.
"""
import json
import os
import random
import time
import zipfile

import numpy as np
import torch
import torchvision
from PIL import Image
from torchvision.models.detection import MaskRCNN_ResNet50_FPN_V2_Weights as Weights
from torchvision.models.detection.anchor_utils import AnchorGenerator
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

FOLD = int(os.environ["AVIA_FOLD"]) if "AVIA_FOLD" in os.environ else None
TRAIN_SEQUENCES = (0, 1, 2, 3, 4, 5)  # 6-8 and 10-12 are never read here (D-001)
INPUT = os.environ.get("AVIA_INPUT", "/kaggle/input")
OUT = os.environ.get("AVIA_OUT", "/kaggle/working")
TMP = os.environ.get("AVIA_TMP", "/kaggle/tmp")
CONFIG = {
    "epochs": int(os.environ.get("AVIA_EPOCHS", 12)),
    "batch_size": int(os.environ.get("AVIA_BATCH", 2)),
    "lr": 0.0025,
    "weight_decay": 1e-4,
    "lr_steps": [8, 11],
    "min_size": int(os.environ.get("AVIA_SIZE", 972)),
    "max_size": int(os.environ.get("AVIA_MAX_SIZE", 1296)),
    "min_mask_area": 16,
    "val_stride": 10,
    "val_score": 0.5,
    "seed": 0,
}
TIME_LIMIT_S = float(os.environ.get("AVIA_TIME_LIMIT_H", 8.5)) * 3600
MAX_STEPS = int(os.environ.get("AVIA_MAX_STEPS", 0))  # 0 = no cap
PRETRAINED = os.environ.get("AVIA_PRETRAINED", "1") == "1"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
START = time.time()


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def train_pair(base):
    """The images/ + instances/ folder holding sequence 0, so testing/ is never picked."""
    for root, dirs, _ in os.walk(base):
        if "images" in dirs and "instances" in dirs:
            if any(n.isdigit() and int(n) == TRAIN_SEQUENCES[0]
                   for n in os.listdir(os.path.join(root, "images"))):
                return root
            dirs.clear()
    return None


def find_root() -> str:
    for base in (INPUT, TMP):
        root = train_pair(base)
        if root:
            return root
    zips = [os.path.join(r, f) for r, _, fs in os.walk(INPUT) for f in fs
            if f == "APPLE_MOTS.zip"]
    if not zips:
        raise SystemExit("APPLE MOTS not attached")
    os.makedirs(TMP, exist_ok=True)
    with zipfile.ZipFile(zips[0]) as z:
        z.extractall(TMP)
    root = train_pair(TMP)
    if root:
        return root
    raise SystemExit("zip has no images/ + instances/ pair with sequence 0")


def sequence_dir(root, kind, sequence):
    for name in os.listdir(os.path.join(root, kind)):
        if name.isdigit() and int(name) == sequence:
            return os.path.join(root, kind, name)
    raise SystemExit(f"sequence {sequence} missing from {kind}/")


def frames_of(root, sequences):
    frames = []
    for s in sequences:
        image_dir, instance_dir = sequence_dir(root, "images", s), sequence_dir(root, "instances", s)
        for name in sorted(os.listdir(image_dir)):
            label = os.path.join(instance_dir, os.path.splitext(name)[0] + ".png")
            if os.path.exists(label):
                frames.append((os.path.join(image_dir, name), label))
    return frames


def load_target(label_path, min_area):
    ids = np.array(Image.open(label_path))
    masks = [ids == v for v in np.unique(ids) if v != 0 and v != 10000]
    masks = [m for m in masks if m.sum() >= min_area]
    boxes = []
    keep = []
    for m in masks:
        ys, xs = np.nonzero(m)
        if xs.max() > xs.min() and ys.max() > ys.min():
            boxes.append([xs.min(), ys.min(), xs.max() + 1, ys.max() + 1])
            keep.append(m)
    if not keep:
        return {"boxes": torch.zeros((0, 4)), "labels": torch.zeros(0, dtype=torch.int64),
                "masks": torch.zeros((0, *ids.shape), dtype=torch.uint8)}
    return {"boxes": torch.tensor(np.array(boxes), dtype=torch.float32),
            "labels": torch.ones(len(keep), dtype=torch.int64),
            "masks": torch.from_numpy(np.stack(keep).astype(np.uint8))}


class Frames(torch.utils.data.Dataset):
    def __init__(self, frames, train):
        self.frames, self.train = frames, train

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, i):
        image_path, label_path = self.frames[i]
        image = np.asarray(Image.open(image_path).convert("RGB"), dtype=np.float32) / 255
        target = load_target(label_path, CONFIG["min_mask_area"])
        tensor = torch.from_numpy(image.copy()).permute(2, 0, 1)
        if self.train:
            tensor = (tensor * random.uniform(0.8, 1.2)).clamp(0, 1)
            if random.random() < 0.5:
                width = tensor.shape[2]
                tensor = tensor.flip(2)
                target["masks"] = target["masks"].flip(2)
                boxes = target["boxes"].clone()
                boxes[:, [0, 2]] = width - target["boxes"][:, [2, 0]]
                target["boxes"] = boxes
        return tensor, target


def collate(batch):
    return tuple(zip(*batch))


def build_model():
    model = torchvision.models.detection.maskrcnn_resnet50_fpn_v2(
        weights=Weights.DEFAULT if PRETRAINED else None, min_size=CONFIG["min_size"],
        max_size=CONFIG["max_size"], box_detections_per_img=300)
    sizes = ((8,), (16,), (32,), (64,), (128,))
    model.rpn.anchor_generator = AnchorGenerator(sizes, ((0.5, 1.0, 2.0),) * 5)
    box_in = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(box_in, 2)
    mask_in = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(mask_in, 256, 2)
    return model


@torch.inference_mode()
def validate(model, frames):
    """Mask F1 at IoU 0.5, greedy by score, on every val_stride-th frame."""
    model.eval()
    tp = fp = fn = 0
    for image_path, label_path in frames[:: CONFIG["val_stride"]]:
        image = np.asarray(Image.open(image_path).convert("RGB"), dtype=np.float32) / 255
        tensor = torch.from_numpy(image.copy()).permute(2, 0, 1).to(DEVICE)
        out = model([tensor])[0]
        keep = out["scores"] >= CONFIG["val_score"]
        pred = (out["masks"][keep, 0] > 0.5).cpu().numpy()
        gt = load_target(label_path, CONFIG["min_mask_area"])["masks"].numpy().astype(bool)
        used = set()
        for p in pred:
            best, best_iou = None, 0.5
            for g in range(len(gt)):
                if g in used:
                    continue
                iou = (p & gt[g]).sum() / max((p | gt[g]).sum(), 1)
                if iou > best_iou:
                    best, best_iou = g, iou
            if best is None:
                fp += 1
            else:
                used.add(best)
                tp += 1
        fn += len(gt) - len(used)
    precision, recall = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
    return {"precision": precision, "recall": recall,
            "f1": 2 * precision * recall / max(precision + recall, 1e-9), "tp": tp, "fp": fp,
            "fn": fn}


def save_model(model, name, metrics):
    torch.save({"model": model.state_dict(), "name": name, "config": CONFIG, "fold": FOLD,
                "metrics": metrics}, os.path.join(OUT, "model.pt"))


def main():
    random.seed(CONFIG["seed"])
    np.random.seed(CONFIG["seed"])
    torch.manual_seed(CONFIG["seed"])
    os.makedirs(OUT, exist_ok=True)
    root = find_root()
    train_seq = [s for s in TRAIN_SEQUENCES if s != FOLD]
    train_frames = frames_of(root, train_seq)
    val_frames = frames_of(root, [FOLD]) if FOLD is not None else []
    log("root", root, "train", len(train_frames), "val", len(val_frames), "device", DEVICE)
    loader = torch.utils.data.DataLoader(
        Frames(train_frames, True), CONFIG["batch_size"], shuffle=True,
        num_workers=2 if DEVICE == "cuda" else 0, collate_fn=collate, drop_last=True)

    model = build_model().to(DEVICE)
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, CONFIG["lr"], momentum=0.9,
                                weight_decay=CONFIG["weight_decay"])
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, CONFIG["lr_steps"], gamma=0.1)
    scaler = torch.amp.GradScaler(enabled=DEVICE == "cuda")
    start_epoch, best_f1 = 0, -1.0
    history = []

    resume = [os.path.join(r, "last.pt") for base in (OUT, INPUT) for r, _, fs in os.walk(base)
              if "last.pt" in fs]
    if resume:
        state = torch.load(resume[0], map_location=DEVICE, weights_only=False)
        model.load_state_dict(state["model"])
        optimizer.load_state_dict(state["optimizer"])
        scheduler.load_state_dict(state["scheduler"])
        scaler.load_state_dict(state["scaler"])
        start_epoch, best_f1, history = state["epoch"], state["best_f1"], state["history"]
        log("resumed from", resume[0], "at epoch", start_epoch)

    name = f"maskrcnn-r50-fpn-{'final' if FOLD is None else f'fold{FOLD}'}"
    steps = 0
    finished = True
    for epoch in range(start_epoch, CONFIG["epochs"]):
        model.train()
        total, count = 0.0, 0
        for images, targets in loader:
            images = [i.to(DEVICE) for i in images]
            targets = [{k: v.to(DEVICE) for k, v in t.items()} for t in targets]
            with torch.amp.autocast(DEVICE, enabled=DEVICE == "cuda"):
                loss = sum(model(images, targets).values())
            optimizer.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(params, 10.0)
            scaler.step(optimizer)
            scaler.update()
            total += float(loss.detach())
            count += 1
            steps += 1
            if count % 50 == 0:
                log("epoch", epoch, "step", count, "loss", round(total / count, 4))
            if time.time() - START > TIME_LIMIT_S or (MAX_STEPS and steps >= MAX_STEPS):
                finished = False
                break
        if not finished:
            break  # the partial epoch is repeated on resume
        scheduler.step()
        record = {"epoch": epoch, "loss": total / max(count, 1)}
        if val_frames:
            record["val"] = validate(model, val_frames)
            if record["val"]["f1"] > best_f1:
                best_f1 = record["val"]["f1"]
                save_model(model, name, record)
        else:
            save_model(model, name, record)  # final run: no validation data by design
        history.append(record)
        log(json.dumps(record))
        torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict(),
                    "scheduler": scheduler.state_dict(), "scaler": scaler.state_dict(),
                    "epoch": epoch + 1, "best_f1": best_f1, "history": history},
                   os.path.join(OUT, "last.pt"))
    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump({"name": name, "fold": FOLD, "finished": finished, "config": CONFIG,
                   "best_val_f1": best_f1 if val_frames else None, "history": history,
                   "device": torch.cuda.get_device_name(0) if DEVICE == "cuda" else "cpu"},
                  f, indent=1)
    log("done, finished =", finished)


if __name__ == "__main__":
    main()
