"""Per-run events and counts.

Event classes (D-012): gt_derived events can be checked against ground-truth tracks;
ranked_only events are ranked suggestions with no ground truth, never accuracy claims.
"""
from dataclasses import dataclass, field

import numpy as np


@dataclass
class EventConfig:
    lost_after: int = 10
    confirm_after: int = 3
    relink_radius: float = 40.0
    relink_window: int = 30
    motion_min_frames: int = 8
    motion_z: float = 4.0


@dataclass
class _State:
    first_frame: int
    last_frame: int
    last_position: tuple[float, float]
    hits: int = 1
    lost: bool = False
    steps: list[float] = field(default_factory=list)


class EventEngine:
    def __init__(self, config: EventConfig | None = None):
        self.config = config or EventConfig()
        self.states: dict[int, _State] = {}
        self.events: list[dict] = []
        self.counts: list[dict] = []

    def _emit(self, frame, track_id, kind, event_class, score, **details):
        self.events.append({"frame": frame, "track_id": track_id, "type": kind,
                            "event_class": event_class, "score": round(float(score), 4),
                            "details": details})

    def update(self, frame: int, positions: dict[int, tuple[float, float]]) -> None:
        c = self.config
        for track_id, position in positions.items():
            state = self.states.get(track_id)
            if state is None:
                self.states[track_id] = _State(frame, frame, position)
                self._check_fragment(frame, track_id, position)
                continue
            if state.lost:
                state.lost = False
                self._emit(frame, track_id, "reappeared", "gt_derived", 1.0,
                           gap=frame - state.last_frame)
            state.steps.append(float(np.hypot(position[0] - state.last_position[0],
                                              position[1] - state.last_position[1])))
            state.last_frame, state.last_position = frame, position
            state.hits += 1
            if state.hits == c.confirm_after:
                self._emit(frame, track_id, "first_seen", "gt_derived", 1.0,
                           first_frame=state.first_frame)
        self._check_motion(frame, positions)
        for track_id, state in self.states.items():
            if not state.lost and frame - state.last_frame >= c.lost_after:
                state.lost = True
                self._emit(frame, track_id, "lost", "gt_derived", 1.0, last_frame=state.last_frame)
        unique = sum(1 for s in self.states.values() if s.hits >= c.confirm_after)
        self.counts.append({"frame": frame, "visible": len(positions), "cumulative_unique": unique})

    def _check_fragment(self, frame, track_id, position):
        """A new track starting where another ended may be the same apple."""
        c = self.config
        for other_id, s in self.states.items():
            gap = frame - s.last_frame
            if other_id == track_id or not 0 < gap <= c.relink_window:
                continue
            distance = float(np.hypot(position[0] - s.last_position[0],
                                      position[1] - s.last_position[1]))
            if distance <= c.relink_radius:
                self._emit(frame, track_id, "possible_fragment", "ranked_only",
                           1 - distance / c.relink_radius, previous_track=other_id, gap=gap)
                return

    def _check_motion(self, frame, positions):
        """Rank tracks that move unlike the others in the frame (robust z-score)."""
        c = self.config
        steps = {t: self.states[t].steps[-1] for t in positions
                 if len(self.states[t].steps) >= c.motion_min_frames}
        if len(steps) < 5:
            return
        values = np.array(list(steps.values()))
        median = np.median(values)
        spread = 1.4826 * np.median(np.abs(values - median)) + 1e-3
        for track_id, step in steps.items():
            z = (step - median) / spread
            if z >= c.motion_z:
                self._emit(frame, track_id, "unusual_motion", "ranked_only", z)

    def summary(self) -> dict:
        last = self.counts[-1] if self.counts else {"cumulative_unique": 0}
        return {"unique_apples": last["cumulative_unique"], "events": len(self.events)}
