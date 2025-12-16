from ipywidgets import jslink, link
from typing import Callable
from anywidget import AnyWidget

def js_sync(
    source: AnyWidget,
    target: AnyWidget,
    keys: list[str],
) -> Callable:
    """Link source and target widgets attributes using on Javascript side.

    Parameters
    ----------
    source : AnyWidget
        Source widget.
    target : AnyWidget
        Target widget.
    keys : list[str]
        List of attributes to link.

    Returns
    -------
    unlink : Callable
        Function to unlink the attributes
    """
    unlinks = {key: jslink((source, key), (target, key)).unlink for key in keys}

    def unlink():
        for unlink in unlinks.values():
            unlink()

    return unlink


def sync(
    source: AnyWidget,
    target: AnyWidget,
    keys: list[str],
) -> Callable:
    """Link source and target widgets attributes using on Python side.

    Parameters
    ----------
    source : AnyWidget
        Source widget.
    target : AnyWidget
        Target widget.
    keys : list[str]
        List of attributes to link.

    Returns
    -------
    unlink : Callable
        Function to unlink the attributes
    """
    unlinks = {key: link((source, key), (target, key)).unlink for key in keys}

    def unlink():
        for unlink in unlinks.values():
            unlink()

    return unlink


