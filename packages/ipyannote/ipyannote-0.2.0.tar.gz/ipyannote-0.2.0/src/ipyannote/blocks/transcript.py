from pathlib import Path
from typing import Callable, Optional

import anywidget
from traitlets import Dict, Float, List, Unicode

from ..utils.sync import js_sync
from .waveform import Waveform


class Transcript(anywidget.AnyWidget):
    _esm = Path(__file__).parent.parent / "static" / "transcript.js"
    _css = Path(__file__).parent.parent / "static" / "transcript.css"

    transcript = List(
        Dict(
            per_key_traits={
                "start": Float(),
                "end": Float(),
                "speaker": Unicode(),
                "text": Unicode(),
            }
        )
    ).tag(sync=True)

    labels = Dict(key_trait=Unicode(), value_trait=Unicode()).tag(sync=True)

    current_time = Float(0.0).tag(sync=True)

    height = Unicode("200px").tag(sync=True)

    def __init__(self, transcript: Optional[list[dict]] = None, height="200px"):
        super().__init__()
        if transcript:
            self.transcript = transcript
        self.height = height

    def sync(self, waveform: Waveform) -> Callable:
        return js_sync(self, waveform, ["labels", "current_time"])
