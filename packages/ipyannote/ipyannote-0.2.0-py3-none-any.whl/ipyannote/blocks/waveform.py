from typing import Callable, Optional
from pathlib import Path

import anywidget

from traitlets import Unicode, Float, Dict, List, Int, Bool
from ..utils.sync import js_sync

import numpy as np
import io
import base64
import scipy.io.wavfile
from pyannote.core import Annotation, Segment


try:
    import torchaudio
except ImportError:
    torchaudio = None


class Waveform(anywidget.AnyWidget):
    _esm = Path(__file__).parent.parent / "static" / "waveform.js"
    _css = Path(__file__).parent.parent / "static" / "waveform.css"

    # used to pass audio to the frontend
    audio_as_base64 = Unicode().tag(sync=True)

    # used to synchronize pool of labels
    labels = Dict(key_trait=Unicode(), value_trait=Unicode()).tag(sync=True)
    color_cycle = Int(0).tag(sync=True)
    active_label = Unicode(None, allow_none=True).tag(sync=True)

    # used to synchronize players
    current_time = Float(0.0).tag(sync=True)
    scroll_time = Float(0.0).tag(sync=True)
    zoom = Float().tag(sync=True)

    playing = Bool(False).tag(sync=True)

    # list of segments
    segments = List(
        Dict(
            per_key_traits={
                "start": Float(),
                "end": Float(),
                "label": Unicode(),
                "id": Unicode(),
                "active": Bool(),
            }
        )
    ).tag(sync=True)
    active_segment = Unicode(None, allow_none=True).tag(sync=True)

    def __init__(
        self,
        audio: Optional[str] = None,
        annotation: Annotation | list[dict] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if audio is not None:
            self.audio = audio
        if annotation is not None:
            self.annotation = annotation

    @staticmethod
    def to_base64(waveform: np.ndarray, sample_rate: int) -> str:
        with io.BytesIO() as content:
            scipy.io.wavfile.write(content, sample_rate, waveform)
            content.seek(0)
            b64 = base64.b64encode(content.read()).decode()
            b64 = f"data:audio/x-wav;base64,{b64}"
        return b64

    @property
    def audio(self) -> str:
        raise NotImplementedError("This is a read-only property")

    @audio.setter
    def audio(self, audio: str):
        # reset annotation when audio changes
        del self.annotation

        if torchaudio is None:
            try:
                sample_rate, waveform = scipy.io.wavfile.read(audio)
            except ValueError:
                raise ValueError(
                    "Please install torchaudio to load audio files other than WAV."
                )
        else:
            waveform, sample_rate = torchaudio.load(audio)
            waveform = waveform.numpy().T

        waveform = waveform.astype(np.float32)
        waveform /= np.max(np.abs(waveform)) + 1e-8
        self.audio_as_base64 = self.to_base64(waveform, sample_rate)

    @audio.deleter
    def audio(self):
        # reset annotation when audio changes
        del self.annotation

        sample_rate = 16000
        waveform = np.zeros((sample_rate,), dtype=np.float32)
        self.audio_as_base64 = self.to_base64(waveform, sample_rate)

    @property
    def annotation(self) -> Annotation:
        annotation = Annotation()
        for region in self.segments:
            segment = Segment(region["start"], region["end"])
            annotation[segment, region["id"]] = region["label"]
        return annotation

    @annotation.setter
    def annotation(self, annotation: Annotation | list[dict]):

        regions = []

        if annotation is None:
            regions = []

        elif isinstance(annotation, list):
            for r, region in enumerate(annotation):
                regions.append(
                    {
                        "start": region["start"],
                        "end": region["end"],
                        "id": region.get("id", f"segment-{r}"),
                        "label": region.get("label", region.get("speaker", "N/A")),
                        "active": False,
                    }
                )

        elif isinstance(annotation, Annotation):
            for segment, track_id, label in annotation.rename_tracks("string").itertracks(yield_label=True):
                regions.append(
                    {
                        "start": segment.start,
                        "end": segment.end,
                        "id": track_id,
                        "label": label,
                        "active": False,
                    }
                )

        else:
            raise ValueError(
                "`annotation` must be either a pyannote.core.Annotation instance or a list of dicts"
            )

        self.segments = regions

    @annotation.deleter
    def annotation(self):
        self.segments = []

    def sync(self, other: "Waveform") -> Callable:
        return js_sync(self, other, ["current_time", "zoom", "scroll_time"])
