from ipywidgets import HBox, VBox
from pyannote.core import Annotation, Segment

from ..blocks.controls import Controls
from ..blocks.labels import Labels
from ..blocks.transcript import Transcript
from ..blocks.waveform import Waveform


class ITranscript(VBox):
    def __init__(
        self,
        audio: str,
        transcript: list[dict],
        diarization: Annotation | None = None,
    ):
        if diarization is None:
            diarization = transcript

        self._diarization = Waveform(audio=audio, annotation=diarization)
        # ... and their common set of speaker labels
        self._labels_speaker = Labels()
        self._labels_speaker.sync(self._diarization)
        # ... and controls
        self._controls = Controls()
        self._controls.sync(self._diarization)

        self._transcript = Transcript(transcript=transcript)
        self._transcript.sync(self._diarization)

        super().__init__(
            [
                self._transcript,
                self._diarization,
                HBox([self._controls, self._labels_speaker]),
            ]
        )
