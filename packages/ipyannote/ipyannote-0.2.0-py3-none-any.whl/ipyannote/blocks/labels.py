from pathlib import Path
from typing import Callable, Optional

import anywidget
from traitlets import Dict, Int, Unicode

from ..utils.sync import js_sync
from .waveform import Waveform

class Labels(anywidget.AnyWidget):
    _esm = Path(__file__).parent.parent / "static" / "labels.js"
    _css = Path(__file__).parent.parent / "static" / "labels.css"

    labels = Dict(key_trait=Unicode(), value_trait=Unicode()).tag(sync=True)
    color_cycle = Int(0).tag(sync=True)
    active_label = Unicode(None, allow_none=True).tag(sync=True)

    def __init__(self, labels: Optional[dict[str, str]] = None):
        super().__init__()
        if labels:
            self.labels = labels

    def sync(self, waveform: Waveform) -> Callable:

        mine = set(self.labels)
        theirs = set(waveform.labels)

        # case where `self` has just been created and does not have any labels yet
        if not mine:
            return js_sync(waveform, self, ["labels", "color_cycle", "active_label"])

        # case where `waveform` labels is a subset of `self` labels
        elif theirs.issubset(mine):
            return js_sync(self, waveform, ["labels", "color_cycle", "active_label"])

        raise ValueError(
            f"Labels do not match: {mine} vs {theirs}. "
        )