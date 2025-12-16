
from pyannote.core import Annotation, Segment
import re


def load_rttm(file_rttm) -> dict[str, Annotation]:
    """Load RTTM file

    Parameter
    ---------
    file_rttm : `str`
        Path to RTTM file.

    Returns
    -------
    annotations : `dict`
        Speaker diarization as a {uri: pyannote.core.Annotation} dictionary.
    """

    annotations = dict()

    with open(file_rttm, "r") as rttm:
        lines = rttm.readlines()
        for l, line in enumerate(lines):
            _, uri, _, start, duration, _, _, label, *_ = line.strip().split(" ")
            start = float(start)
            duration = float(duration)
            segment = Segment(float(start), float(start) + float(duration))
            annotations.setdefault(uri, Annotation(uri=uri))[segment, str(l)] = label

    return annotations


def load_stm(file_stm) -> dict[str, list[dict]]:
    """Load STM file

    Parameter
    ---------
    file_stm : `str`
        Path to STM file.

    Returns
    -------
    transcripts :
        Transcript as a {uri: list of dict} dictionary.
        Each dict contains 'start', 'end', 'speaker', and 'text' keys.
    """

    transcript = dict()

    with open(file_stm, "r") as stm:
        lines = stm.readlines()
        for line in lines:
            if line.startswith(";;"):
                continue
            uri, _, speaker, start, end, _, *words = re.split(r"\s+", line.strip())
            text = " ".join(words)

            transcript.setdefault(uri, list()).append(
                {
                    "start": float(start),
                    "end": float(end),
                    "speaker": speaker,
                    "text": text,
                }
            )

    return transcript


