import importlib.metadata

from ipywidgets import HBox, VBox
from pyannote.core import Annotation

from .blocks.controls import Controls
from .blocks.labels import Labels
from .blocks.waveform import Waveform

try:
    __version__ = importlib.metadata.version("ipyannote")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"


class IAnnotation(VBox):
    def __init__(self, audio: str, annotation: Annotation):
        self._waveform = Waveform(audio=audio, annotation=annotation)

        self._controls = Controls()
        self._controls.sync(self._waveform)

        self._labels = Labels()
        self._labels.sync(self._waveform)

        super().__init__([self._waveform, HBox([self._controls, self._labels])])

    @property
    def annotation(self) -> Annotation:
        return self._waveform.annotation

    @annotation.setter
    def annotation(self, annotation: Annotation):
        self._waveform.annotation = annotation

    @annotation.deleter
    def annotation(self):
        del self._waveform.annotation
