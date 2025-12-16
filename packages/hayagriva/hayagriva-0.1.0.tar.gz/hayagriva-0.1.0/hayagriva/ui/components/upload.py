"""Upload component for the Gradio UI."""
from __future__ import annotations

import importlib.util
from typing import Callable
import gradio as gr
from hayagriva.exceptions import MissingDependencyError


def uploader(on_upload):
    with gr.Column():
        gr.Markdown("### Ingest Text")

        text_input = gr.Textbox(
            label="Paste text to ingest",
            lines=8,
            placeholder="Paste or type text here...",
        )

        ingest_btn = gr.Button("Ingest Data")

        output = gr.Markdown()

        ingest_btn.click(
            fn=on_upload,
            inputs=[text_input],
            outputs=[output],
        )