"""Settings component placeholder."""
from __future__ import annotations

import importlib.util

from hayagriva.exceptions import MissingDependencyError


def settings_panel():
    if importlib.util.find_spec("gradio") is None:
        raise MissingDependencyError("gradio is required for the UI. Install with `pip install gradio`.")
    import gradio as gr

    return gr.Markdown("## Settings\nFuture controls for models, vector stores, and retrieval options.")
