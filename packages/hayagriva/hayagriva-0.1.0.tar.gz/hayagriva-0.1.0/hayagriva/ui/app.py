"""Gradio application for Hayagriva."""
from __future__ import annotations

import importlib.util
from typing import Optional

from hayagriva.core.hayagriva import Hayagriva
from hayagriva.ui.components.chat import chat_box
from hayagriva.ui.components.settings import settings_panel
from hayagriva.ui.components.upload import uploader
from hayagriva.utils.logger import get_logger

logger = get_logger(__name__)


def launch_ui(rag: Optional[Hayagriva] = None, port: int = 7878, share: bool = False) -> None:
    """Launch a minimal Gradio interface."""

    if importlib.util.find_spec("gradio") is None:
        raise RuntimeError("Gradio dependency is missing. Install with `pip install gradio`.")
    import gradio as gr

    rag = rag or Hayagriva()

    def on_upload(text, *args):
        rag.add_documents([text])
        return f"Ingested text. Index size: {rag.get_index_size()}"

    def on_submit(message, history=None):
        for token in rag.ask(message):
            yield token

    with gr.Blocks() as demo:
        gr.Markdown("# Hayagriva RAG\nIngest text and ask questions.")
        with gr.Row():
            with gr.Column():
                uploader(on_upload)
                settings_panel()
            with gr.Column():
                chatbot, msg = chat_box(on_submit)

    logger.info("Launching Gradio UI on port %d", port)
    demo.launch(server_name="0.0.0.0", server_port=port, share=share)