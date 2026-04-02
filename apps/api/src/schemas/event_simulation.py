from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


EXECUTION_WINDOWS = (
    "pre_open",
    "open_5m",
    "morning_30m",
    "midday_reprice",
    "afternoon_follow",
    "close_positioning",
)

EXECUTION_WINDOW_LABELS = {
    "pre_open": "盘前定价",
    "open_5m": "开盘 5 分钟",
    "morning_30m": "早盘 30 分钟",
    "midday_reprice": "午间重定价",
    "afternoon_follow": "午后跟随",
    "close_positioning": "收盘前仓位调整",
}


@dataclass(frozen=True, slots=True)
class ExecutionWindowDefinition:
    window_id: str
    label: str
    order: int
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CloneTimingProfile:
    participant_id: str
    participant_family: str
    role: str
    preferred_execution_windows: list[str] = field(default_factory=list)
    avoid_execution_windows: list[str] = field(default_factory=list)
    timing_reason_codes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EventExecutionClock:
    event_id: str
    current_window: str
    current_order: int
    status: str
    windows: list[ExecutionWindowDefinition] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["windows"] = [window.to_dict() for window in self.windows]
        return payload


def normalize_execution_windows(values: list[str] | tuple[str, ...] | None) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        marker = str(value or "").strip().lower()
        if not marker:
            continue
        if marker not in EXECUTION_WINDOWS:
            supported = ", ".join(EXECUTION_WINDOWS)
            raise ValueError(f"Unsupported execution window '{value}'. Supported windows: {supported}.")
        if marker in seen:
            continue
        seen.add(marker)
        normalized.append(marker)
    return normalized


def build_default_execution_clock(event_id: str) -> EventExecutionClock:
    windows = [
        ExecutionWindowDefinition(
            window_id=window_id,
            label=EXECUTION_WINDOW_LABELS[window_id],
            order=index,
            description=f"{EXECUTION_WINDOW_LABELS[window_id]}阶段的 clone 行为窗口。",
        )
        for index, window_id in enumerate(EXECUTION_WINDOWS, start=1)
    ]
    return EventExecutionClock(
        event_id=event_id,
        current_window=EXECUTION_WINDOWS[0],
        current_order=1,
        status="ready",
        windows=windows,
    )


def build_clone_timing_profile(*, participant_id: str, participant_family: str, role: str) -> CloneTimingProfile:
    preferred: list[str]
    avoid: list[str]
    if role == "first_move":
        preferred = ["pre_open", "open_5m", "morning_30m"]
        avoid = ["close_positioning"]
    elif role == "follow_on":
        preferred = ["morning_30m", "midday_reprice", "afternoon_follow"]
        avoid = ["pre_open"]
    else:
        preferred = ["midday_reprice", "close_positioning"]
        avoid = ["open_5m"]

    family_overrides = {
        "retail_fast_money": (["open_5m", "morning_30m"], ["close_positioning"]),
        "institution_confirmation": (["pre_open", "open_5m"], ["close_positioning"]),
        "industry_research": (["morning_30m", "midday_reprice"], ["pre_open"]),
        "policy_research": (["midday_reprice", "close_positioning"], ["open_5m"]),
        "quant_risk_budget": (["open_5m", "afternoon_follow"], ["pre_open"]),
        "risk_control": (["midday_reprice", "close_positioning"], ["open_5m"]),
        "media_sentiment": (["open_5m", "afternoon_follow"], ["close_positioning"]),
        "supply_chain_channel": (["pre_open", "morning_30m"], ["close_positioning"]),
    }
    if participant_family in family_overrides:
        preferred, avoid = family_overrides[participant_family]

    preferred_windows = normalize_execution_windows(preferred)
    avoid_windows = normalize_execution_windows(avoid)
    return CloneTimingProfile(
        participant_id=participant_id,
        participant_family=participant_family,
        role=role,
        preferred_execution_windows=preferred_windows,
        avoid_execution_windows=avoid_windows,
        timing_reason_codes=[
            f"timing_role:{role}",
            f"timing_family:{participant_family}",
            f"timing_preferred:{','.join(preferred_windows)}",
        ],
    )
