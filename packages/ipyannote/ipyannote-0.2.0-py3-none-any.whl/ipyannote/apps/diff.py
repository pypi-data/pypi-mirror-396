from ipywidgets import VBox, HBox
from pyannote.core import Annotation
from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.metrics.errors.identification import IdentificationErrorAnalysis

from ..blocks.labels import Labels
from ..blocks.waveform import Waveform
from ..blocks.controls import Controls

class AnnotationDiff(VBox):
    def __init__(
        self,
        audio: str,
        reference: Annotation,
        hypothesis: Annotation,
        permutation_invariant: bool = False,
    ):
        self.permutation_invariant = permutation_invariant

        # create (empty) reference and hypothesis waveforms...
        self._waveform_reference = Waveform(audio=audio)
        self._waveform_hypothesis = Waveform(audio=audio)
        # ... and their common set of speaker labels
        self._labels_speaker = Labels()
        self._labels_speaker.sync(self._waveform_reference)
        self._labels_speaker.sync(self._waveform_hypothesis)
        #... and controls
        self._controls = Controls()
        self._controls.sync(self._waveform_reference)

        # create (empty) error waveform...
        self._waveform_diff = Waveform(audio=audio)
        # ... and its set of error labels
        self._labels_diff = Labels(
            {
                "false alarm": "#00ff00",
                "missed detection": "#ffa500",
                "confusion": "#ff0000",
            }
        )
        self._labels_diff.sync(self._waveform_diff)

        super().__init__(
            [
                self._labels_speaker,
                self._waveform_reference,
                self._waveform_hypothesis,
                self._waveform_diff,
                HBox([self._controls, self._labels_diff]),
            ]
        )

        # synchronize players
        self._waveform_hypothesis.sync(self._waveform_reference)
        self._waveform_diff.sync(self._waveform_reference)

        if self.permutation_invariant:
            # map hypothesis labels to reference labels...
            _hypothesis = self._match_speakers(reference, hypothesis)
        else:
            _hypothesis = hypothesis
        # ... and compute errors
        errors = self._compute_errors(reference, _hypothesis)

        # populate reference, hypothesis and errors waveforms
        self._waveform_reference.annotation = reference
        self._waveform_hypothesis.annotation = _hypothesis
        self._waveform_diff.annotation = errors

    def _match_speakers(
        self, reference: Annotation, hypothesis: Annotation
    ) -> Annotation:
        mapping = {label: f"@{label}" for label in hypothesis.labels()}
        hypothesis = hypothesis.rename_labels(mapping)

        optimal_mapping = DiarizationErrorRate().optimal_mapping
        mapping = optimal_mapping(reference, hypothesis)
        mapped_hypothesis = hypothesis.rename_labels(mapping)
        return mapped_hypothesis

    def _compute_errors(
        self, reference: Annotation, mapped_hypothesis: Annotation
    ) -> Annotation:
        errors: Annotation = IdentificationErrorAnalysis().difference(
            reference, mapped_hypothesis
        ).support()

        # only keep error types
        mapping = {error: error[0] for error in errors.labels()}
        errors = errors.rename_labels(mapping).subset(["correct"], invert=True)
        return errors.rename_tracks()
