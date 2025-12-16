from pathlib import Path
from typing import Callable, Optional

import anywidget
from ipywidgets import jslink
from traitlets import Dict, Float, List, Unicode


class HorizontalTranscript(anywidget.AnyWidget):
    """Display transcript segments in a horizontal layout.

    Parameters
    ----------
    transcript : list of dict, optional
        List of segments with keys: 'start', 'end', 'speaker', 'text'
    width : str, optional
        Width of the widget.
        Defaults to take 100% of the available space.
    """

    _esm = Path(__file__).parent.parent / "static" / "horizontal_transcript.js"
    _css = Path(__file__).parent.parent / "static" / "horizontal_transcript.css"

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

    width = Unicode("100%").tag(sync=True)

    def __init__(self, transcript: Optional[list[dict]] = None, width: str = "100%"):
        super().__init__()

        self.transcript = transcript or []
        self.width = width

    def _jslink(
        self,
        other: "Waveform",
        keys: list[str] = [],
    ) -> Callable:
        """Link attributes with other waveform

        Parameters
        ----------
        other : Waveform
            The other Waveform widget
        keys : list[str]
            List of attributes to link

        Returns
        -------
        unlink : Callable
            Function to unlink the attributes
        """
        unlinks = {key: jslink((self, key), (other, key)).unlink for key in keys}

        def unlink():
            for unlink in unlinks.values():
                unlink()

        return unlink

    def js_sync_player(self, other: "Waveform") -> Callable:
        """Link transcript widget to a waveform

        Parameters
        ----------
        other: Waveform
            Waveform to link to transcript

        Returns
        -------
        unlink: Callable
            Function to unlink the attributes
        """
        return self._jslink(other, ["current_time", "labels"])
