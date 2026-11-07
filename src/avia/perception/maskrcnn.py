"""Mask R-CNN R50-FPN with small anchors (baseline, T24)."""
import numpy as np

from avia.types import Detection, resolve_overlaps


def build_model(num_classes: int = 2, min_size: int = 972, max_size: int = 1296,
                pretrained: bool = False):
    import torchvision
    from torchvision.models.detection import MaskRCNN_ResNet50_FPN_V2_Weights as W
    from torchvision.models.detection.anchor_utils import AnchorGenerator
    from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
    from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

    model = torchvision.models.detection.maskrcnn_resnet50_fpn_v2(
        weights=W.DEFAULT if pretrained else None, min_size=min_size, max_size=max_size,
        box_detections_per_img=300)
    sizes = ((8,), (16,), (32,), (64,), (128,))
    model.rpn.anchor_generator = AnchorGenerator(sizes, ((0.5, 1.0, 2.0),) * 5)
    box_in = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(box_in, num_classes)
    mask_in = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(mask_in, 256, num_classes)
    return model


class MaskRCNNDetector:
    trained = True

    def __init__(self, checkpoint: str, score_floor: float = 0.1, device: str | None = None):
        import torch

        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        ckpt = torch.load(checkpoint, map_location="cpu", weights_only=False)
        config = ckpt.get("config", {})
        self.model = build_model(min_size=config.get("min_size", 972),
                                 max_size=config.get("max_size", 1296))
        self.model.load_state_dict(ckpt["model"])
        self.model.to(self.device).eval()
        self.name = ckpt.get("name", "maskrcnn-r50-fpn")
        self.score_floor = score_floor

    def detect(self, image_bgr: np.ndarray) -> list[Detection]:
        torch = self.torch
        rgb = image_bgr[:, :, ::-1].copy()
        tensor = torch.from_numpy(rgb).permute(2, 0, 1).float().div(255).to(self.device)
        with torch.inference_mode():
            out = self.model([tensor])[0]
        keep = out["scores"] >= self.score_floor
        masks = (out["masks"][keep, 0] > 0.5).cpu().numpy()
        scores = out["scores"][keep].cpu().numpy().tolist()
        return resolve_overlaps([Detection(m, s) for m, s in zip(masks, scores)])
